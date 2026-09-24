"""eSewa ePayment v2 (RC) — offline HMAC verification + status lookup (Phase 5+).

Redirect flow:
  backend /initiate → signed form fields → browser POSTs to eSewa RC →
  eSewa redirects browser to success_url?data=<base64 JSON> →
  frontend forwards `data` to backend /verify →
  backend checks HMAC signature + status COMPLETE + amount match,
  then queries the eSewa transaction-status API as the final authority.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.services.payments.base import InitiateResult, PaymentError, PaymentProvider

log = logging.getLogger("eventflow.payments")

REQUEST_SIGNED_FIELDS = "total_amount,transaction_uuid,product_code"


def _sign(message: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def sign_fields(fields: dict[str, Any], signed_field_names: str, secret: str) -> str:
    message = ",".join(f"{k}={fields[k]}" for k in signed_field_names.split(","))
    return _sign(message, secret)


class EsewaProvider(PaymentProvider):
    name = "ESEWA"

    def __init__(self, merchant_code: str | None = None, secret_key: str | None = None,
                 base_url: str | None = None):
        self.merchant_code = merchant_code or settings.ESEWA_MERCHANT_CODE
        self.secret_key = secret_key or settings.ESEWA_SECRET_KEY
        self.base_url = (base_url or settings.ESEWA_BASE_URL).rstrip("/")

    def initiate(self, *, amount: float, transaction_id: str, registration_id: int,
                 event_title: str, return_urls: dict[str, str]) -> InitiateResult:
        total = f"{amount:.2f}"
        fields = {
            "amount": total,
            "tax_amount": "0",
            "total_amount": total,
            "transaction_uuid": transaction_id,
            "product_code": self.merchant_code,
            "product_service_charge": "0",
            "product_delivery_charge": "0",
            "success_url": return_urls["success_url"],
            "failure_url": return_urls["failure_url"],
            "signed_field_names": REQUEST_SIGNED_FIELDS,
        }
        fields["signature"] = sign_fields(fields, REQUEST_SIGNED_FIELDS, self.secret_key)
        return InitiateResult(
            provider=self.name, transaction_id=transaction_id, amount=amount,
            action_url=f"{self.base_url}/api/epay/main/v2/form",
            fields=fields,
            extra={"event_title": event_title, "registration_id": registration_id},
        )

    def verify(self, *, expected_amount: float, transaction_id: str,
               payload: dict[str, Any]) -> dict[str, Any]:
        log.info("[eSewa] PAYMENT_RETURNED transaction_uuid=%s", transaction_id)
        raw = payload.get("data")
        if not raw:
            raise PaymentError("Missing eSewa response data", 400)
        # Belt-and-braces: unencoded `+` in the query becomes a space en route.
        raw = raw.replace(" ", "+")
        try:
            decoded = json.loads(base64.b64decode(raw).decode())
        except Exception:
            raise PaymentError("Invalid eSewa response encoding", 400)
        log.info("[eSewa] PAYMENT_RESPONSE_DECODED status=%s total_amount=%s",
                 decoded.get("status"), decoded.get("total_amount"))
        if decoded.get("status") != "COMPLETE":
            raise PaymentError(f"eSewa payment not complete (status={decoded.get('status')})", 402)
        signed = decoded.get("signed_field_names", "")
        if not signed:
            raise PaymentError("eSewa response missing signature", 400)
        try:
            expected_sig = sign_fields(decoded, signed, self.secret_key)
        except KeyError as e:
            raise PaymentError(f"eSewa response missing field {e}", 400)
        if not hmac.compare_digest(expected_sig, decoded.get("signature", "")):
            raise PaymentError("eSewa signature mismatch — possible tampering", 400)
        log.info("[eSewa] PAYMENT_SIGNATURE_VERIFIED transaction_uuid=%s", transaction_id)
        if decoded.get("transaction_uuid") != transaction_id:
            raise PaymentError("eSewa transaction mismatch", 400)
        try:
            paid = float(str(decoded.get("total_amount", "0")).replace(",", ""))
        except ValueError:
            raise PaymentError("eSewa amount unreadable", 400)
        if abs(paid - float(expected_amount)) > 0.009:
            raise PaymentError(f"Amount mismatch: expected {expected_amount}, got {paid}", 400)
        self._status_lookup(transaction_id, paid)
        return {
            "transaction_code": decoded.get("transaction_code"),
            "status": decoded.get("status"),
            "total_amount": paid,
            "transaction_uuid": decoded.get("transaction_uuid"),
        }

    def recheck(self, *, expected_amount: float, transaction_id: str) -> dict[str, Any]:
        """Status-lookup-only verification (no redirect data needed).

        Used when the buyer completed payment but the redirect never reached
        us: eSewa itself is the source of truth here.
        """
        log.info("[eSewa] RECHECK transaction_uuid=%s", transaction_id)
        receipt = self._status_lookup(transaction_id, expected_amount)
        return {
            "transaction_code": (receipt or {}).get("transaction_code"),
            "status": "COMPLETE",
            "total_amount": float(expected_amount),
            "transaction_uuid": transaction_id,
            "via": "recheck",
        }
    def _status_lookup(self, transaction_id: str, amount: float) -> dict | None:
        """Final authority: eSewa transaction-status API. Fail closed.

        eSewa matches total_amount exactly as paid — docs show plain integers
        ("100") while forms carry decimals ("100.00"), so both formats are
        tried before giving up. Returns the status body on COMPLETE.
        """
        formats = []
        for fmt in (("%g" % amount), ("%.2f" % float(amount))):
            if fmt not in formats:
                formats.append(fmt)
        if not settings.ESEWA_STATUS_CHECK:
            log.info("[eSewa] status lookup skipped (ESEWA_STATUS_CHECK=false)")
            return
        last_error = None
        for total in formats:
            url = (f"{self.base_url}/api/epay/transaction/status/"
                   f"?product_code={self.merchant_code}&total_amount={total}"
                   f"&transaction_uuid={transaction_id}")
            log.info("[eSewa] PAYMENT_VERIFICATION_REQUEST transaction_uuid=%s total_amount=%s",
                     transaction_id, total)
            try:
                resp = httpx.get(url, timeout=15)
            except httpx.HTTPError as e:
                log.warning("[eSewa] status lookup unreachable: %s", e)
                last_error = PaymentError("Could not verify transaction with eSewa. Please try again shortly.", 502)
                continue
            try:
                body = resp.json()
            except Exception:
                last_error = PaymentError("eSewa status response unreadable", 502)
                continue
            status = (body.get("status") or "").upper()
            log.info("[eSewa] PAYMENT_VERIFICATION_RESULT status=%s", status)
            if status == "COMPLETE":
                try:
                    reported = float(str(body.get("total_amount", amount)).replace(",", ""))
                except ValueError:
                    reported = float(amount)
                if abs(reported - float(amount)) > 0.009:
                    raise PaymentError("eSewa amount mismatch", 400)
                return body
            if status in ("PENDING", "AMBIGUOUS"):
                last_error = PaymentError("Payment is being verified. Please check again shortly.", 402)
                continue
            if status in ("NOT_FOUND", "CANCELED", "CANCELLED", "FAILED"):
                last_error = PaymentError(
                    f"eSewa reports transaction status={status or 'unknown'}. Ticket not created.", 402)
                continue
            last_error = PaymentError(
                f"eSewa reports transaction status={status or 'unknown'}. Ticket not created.", 402)
        raise last_error or PaymentError("eSewa transaction could not be verified", 502)


def build_test_response(*, transaction_id: str, amount: float,
                        merchant_code: str | None = None,
                        secret_key: str | None = None,
                        status: str = "COMPLETE") -> str:
    """Craft a signed eSewa-style response (tests / local UAT simulation only)."""
    secret_key = secret_key or settings.ESEWA_SECRET_KEY
    merchant_code = merchant_code or settings.ESEWA_MERCHANT_CODE
    fields = {
        "transaction_code": "000TEST",
        "status": status,
        "total_amount": f"{amount:.2f}",
        "transaction_uuid": transaction_id,
        "product_code": merchant_code,
        "signed_field_names": "transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names",
    }
    fields["signature"] = sign_fields(fields, fields["signed_field_names"], secret_key)
    return base64.b64encode(json.dumps(fields).encode()).decode()
