"""Khalti ePayment v2 (test) — server-side lookup verification (Phase 5).

Redirect flow:
  backend /initiate → Khalti API (secret key stays here) → {pidx, payment_url} →
  browser pays → Khalti redirects to return_url?pidx=… →
  frontend forwards pidx to backend /verify →
  backend calls Khalti lookup API → status must be Completed + amount match.

Without a real Khalti test key, initiation honestly fails (never faked).
"""
from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.services.payments.base import InitiateResult, PaymentError, PaymentProvider

PLACEHOLDER_KEYS = {"", "test_secret_key", "test_secret_key_change_me", "changeme"}


class KhaltiProvider(PaymentProvider):
    name = "KHALTI"

    def __init__(self, secret_key: str | None = None, base_url: str | None = None):
        self.secret_key = secret_key or settings.KHALTI_SECRET_KEY
        self.base_url = (base_url or settings.KHALTI_BASE_URL).rstrip("/")

    def _configured(self) -> bool:
        return bool(self.secret_key) and self.secret_key.strip() not in PLACEHOLDER_KEYS

    def initiate(self, *, amount: float, transaction_id: str, registration_id: int,
                 event_title: str, return_urls: dict[str, str]) -> InitiateResult:
        if not self._configured():
            raise PaymentError(
                "Khalti test key not configured. Set KHALTI_SECRET_KEY to a Khalti sandbox key.", 400
            )
        paisa = int(round(float(amount) * 100))
        if paisa <= 0:
            raise PaymentError("Invalid amount for Khalti", 400)
        try:
            resp = httpx.post(
                f"{self.base_url}/epayment/initiate/",
                json={
                    "return_url": return_urls["success_url"],
                    "website_url": settings.FRONTEND_URL,
                    "amount": paisa,
                    "purchase_order_id": transaction_id,
                    "purchase_order_name": f"EventFlow registration {registration_id}: {event_title[:60]}",
                },
                headers={"Authorization": f"Key {self.secret_key}"},
                timeout=15,
            )
        except httpx.HTTPError as e:
            raise PaymentError(f"Khalti unreachable: {e}", 502)
        if resp.status_code != 200:
            raise PaymentError(f"Khalti rejected initiation (HTTP {resp.status_code})", 502)
        body = resp.json()
        if not body.get("pidx") or not body.get("payment_url"):
            raise PaymentError("Khalti initiation malformed", 502)
        return InitiateResult(
            provider=self.name, transaction_id=transaction_id, amount=amount,
            payment_url=body["payment_url"],
            extra={"pidx": body["pidx"], "expires_at": body.get("expires_at")},
        )

    def recheck(self, *, expected_amount: float, pidx: str) -> dict[str, Any]:
        """Lookup-only verification using a stored pidx (no redirect data)."""
        return self.verify(expected_amount=expected_amount, transaction_id="",
                           payload={"pidx": pidx})

    def verify(self, *, expected_amount: float, transaction_id: str,
               payload: dict[str, Any]) -> dict[str, Any]:
        if not self._configured():
            raise PaymentError("Khalti test key not configured", 400)
        pidx = payload.get("pidx")
        if not pidx:
            raise PaymentError("Missing Khalti pidx", 400)
        try:
            resp = httpx.post(
                f"{self.base_url}/epayment/lookup/",
                json={"pidx": pidx},
                headers={"Authorization": f"Key {self.secret_key}"},
                timeout=15,
            )
        except httpx.HTTPError as e:
            raise PaymentError(f"Khalti unreachable: {e}", 502)
        if resp.status_code != 200:
            raise PaymentError(f"Khalti lookup failed (HTTP {resp.status_code})", 502)
        body = resp.json()
        if body.get("status") != "Completed":
            raise PaymentError(f"Khalti payment not completed (status={body.get('status')})", 402)
        paid_paisa = body.get("total_amount")
        if paid_paisa is None or int(paid_paisa) != int(round(float(expected_amount) * 100)):
            raise PaymentError("Khalti amount mismatch", 400)
        return {
            "pidx": pidx,
            "transaction_id": body.get("transaction_id"),
            "status": body.get("status"),
            "total_amount": float(paid_paisa) / 100,
        }
