"""Payments — Phase 5 (initiate → provider → server-side verify → ticket).

The browser is NEVER trusted: COMPLETED + CONFIRMED happen only after the
backend verifies with the provider (eSewa HMAC / Khalti lookup). Callbacks are
idempotent — re-verifying returns the existing ticket, never a duplicate.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import rate_limit, require_auth
from app.core.config import settings
from app.database import get_db
from app.models.event import Event
from app.models.finance import Payment, PaymentProvider as ProviderEnum, PaymentStatus
from app.models.ticket import Registration, TicketType
from app.models.user import User as UserModel
from app.services.booking import confirm_booking
from app.services.payments import PaymentError, get_provider
from app.services.wallet import get_wallet_view, record_ticket_sale

log = logging.getLogger("eventflow.payments")

api_router = APIRouter(prefix="/payments", tags=["Payments"])


def _own_pending(db: Session, user: UserModel, registration_id: int) -> Registration:
    try:
        registration_id = int(registration_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid registration_id")
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    if reg.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    return reg


def _amount_for(db: Session, reg: Registration) -> float:
    tt = db.query(TicketType).filter(TicketType.id == reg.ticket_type_id).first()
    return float(tt.price or 0.0) if tt else 0.0


def _ticket_payload(db: Session, reg: Registration) -> dict:
    from app.models.ticket import Ticket

    t = db.query(Ticket).filter(Ticket.registration_id == reg.id).first()
    return {
        "ticket_id": t.id if t else None,
        "ticket_code": t.ticket_code if t else None,
        "qr_token": t.qr_token if t else None,
        "qr_code_url": t.qr_code_url if t else None,
    }


@api_router.post("/initiate", response_model=dict, dependencies=[Depends(rate_limit(30, 60))])
def initiate_payment(payload: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    provider_name = (payload.get("provider") or "").upper()
    try:
        provider = get_provider(provider_name)
    except PaymentError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    reg = _own_pending(db, user, payload.get("registration_id"))
    if str(getattr(reg.status, "value", reg.status)) == "CONFIRMED":
        return {"success": True, "message": "Already paid", "data": {"already": True, **_ticket_payload(db, reg)}}
    if str(getattr(reg.status, "value", reg.status)) == "CANCELLED":
        raise HTTPException(status_code=400, detail="Order was cancelled")
    amount = _amount_for(db, reg)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="This order needs no payment (free event)")

    # eSewa demands a UNIQUE transaction_uuid on EVERY payment attempt, so each
    # initiate mints a fresh PENDING row + fresh uuid. Prior PENDING rows for
    # the same order are retired (superseded) — never reused, never double-sent.
    for stale in db.query(Payment).filter(
            Payment.registration_id == reg.id,
            Payment.provider == ProviderEnum[provider_name],
            Payment.status == PaymentStatus.PENDING).all():
        stale.status = PaymentStatus.FAILED
        stale.provider_response = {**(stale.provider_response or {}),
                                   "note": "Superseded by a fresh attempt"}
    transaction_id = f"evt-pay-{uuid.uuid4()}"
    payment = Payment(
        registration_id=reg.id, provider=ProviderEnum[provider_name],
        transaction_id=transaction_id, amount=amount, currency="NPR",
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    try:
        db.commit()
    except Exception:
        # UNIQUE(transaction_uuid) collision is astronomically unlikely;
        # retry once with a new uuid rather than failing the checkout.
        db.rollback()
        transaction_id = f"evt-pay-{uuid.uuid4()}"
        payment = Payment(
            registration_id=reg.id, provider=ProviderEnum[provider_name],
            transaction_id=transaction_id, amount=amount, currency="NPR",
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        db.commit()
    db.refresh(payment)
    log.info("[eSewa] New payment registration_id=%s amount=%s", reg.id, amount)
    log.info("[eSewa] transaction_uuid: %s", transaction_id)

    ev = db.query(Event).filter(Event.id == reg.event_id).first()
    base = f"{settings.FRONTEND_URL.rstrip('/')}/payments/callback"
    urls = {
        "success_url": f"{base}?provider={provider_name}&reg={reg.id}",
        "failure_url": f"{base}?provider={provider_name}&reg={reg.id}&failed=1",
    }
    try:
        result = provider.initiate(
            amount=amount, transaction_id=transaction_id, registration_id=reg.id,
            event_title=ev.title if ev else f"Registration {reg.id}", return_urls=urls,
        )
    except PaymentError as e:
        payment.status = PaymentStatus.FAILED
        payment.provider_response = {"error": str(e)}
        db.commit()
        raise HTTPException(status_code=e.status_code, detail=str(e))
    payment.provider_response = {"initiate": result.extra or {}}
    db.commit()
    log.info("[Payment] PAYMENT_INITIATED provider=%s registration=%s transaction=%s amount=%s",
             provider_name, reg.id, transaction_id, amount)
    out = {"provider": provider_name, "transaction_id": transaction_id, "amount": amount,
           "payment_id": payment.id}
    if result.action_url:
        out["action_url"] = result.action_url
        out["fields"] = result.fields
    if result.payment_url:
        out["payment_url"] = result.payment_url
        out["extra"] = result.extra
    return {"success": True, "message": f"Redirect to {provider_name}", "data": out}


@api_router.post("/verify", response_model=dict, dependencies=[Depends(rate_limit(30, 60))])
def verify_payment(payload: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    provider_name = (payload.get("provider") or "").upper()
    reg = _own_pending(db, user, payload.get("registration_id"))
    if not provider_name:
        # Recheck without provider: use the latest payment attempt's provider.
        latest = (
            db.query(Payment).filter(Payment.registration_id == reg.id)
            .order_by(Payment.id.desc()).first()
        )
        if not latest:
            raise HTTPException(status_code=400, detail="No payment initiated for this order")
        provider_name = str(getattr(latest.provider, "value", latest.provider))
    try:
        provider = get_provider(provider_name)
    except PaymentError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    payment = (
        db.query(Payment)
        .filter(Payment.registration_id == reg.id, Payment.provider == ProviderEnum[provider_name])
        .order_by(Payment.id.desc())
        .first()
    )
    if payment and str(getattr(payment.status, "value", payment.status)) == "COMPLETED":
        return {"success": True, "message": "Payment already verified",
                "data": {"already": True, **_ticket_payload(db, reg)}}
    if not payment:
        raise HTTPException(status_code=400, detail="No payment initiated for this order")
    if str(getattr(reg.status, "value", reg.status)) == "CANCELLED":
        raise HTTPException(status_code=400, detail="Order was cancelled")

    amount = _amount_for(db, reg)
    # Recheck mode: no redirect data (user paid but never returned). Verify
    # against the provider using stored references only.
    recheck = not payload.get("data") and not payload.get("pidx")
    try:
        if recheck:
            log.info("[Payment] RECHECK registration=%s provider=%s", reg.id, provider_name)
            if provider_name == "ESEWA":
                receipt = provider.recheck(expected_amount=amount,
                                           transaction_id=payment.transaction_id)
            elif provider_name == "KHALTI":
                pidx = (payment.provider_response or {}).get("initiate", {}).get("pidx")
                if not pidx:
                    raise PaymentError("No Khalti transaction to recheck", 400)
                receipt = provider.recheck(expected_amount=amount, pidx=pidx)
            else:
                raise PaymentError("Recheck not supported for this provider", 400)
        else:
            receipt = provider.verify(expected_amount=amount,
                                      transaction_id=payment.transaction_id, payload=payload)
    except PaymentError as e:
        # PENDING/AMBIGUOUS stays retryable; definitive failures close the attempt.
        if not (e.status_code == 402 and "being verified" in str(e)):
            payment.status = PaymentStatus.FAILED
            payment.provider_response = {**(payment.provider_response or {}), "verify_error": str(e)}
            db.commit()
        raise HTTPException(status_code=e.status_code, detail=str(e))

    payment.status = PaymentStatus.COMPLETED
    payment.provider_response = {**(payment.provider_response or {}), "receipt": receipt}
    db.flush()
    # Atomic: payment + registration + ticket + ledger commit together.
    # Any failure rolls back to PENDING (never half-COMPLETE without a ticket).
    try:
        from app.services.booking import BookingError
        out = confirm_booking(db, reg, amount, commit=False)
        ev = db.query(Event).filter(Event.id == reg.event_id).first()
        if ev:
            record_ticket_sale(db, organizer_id=ev.organizer_id, registration_id=reg.id,
                               gross=amount, commit=False)
        db.commit()
    except Exception as e:
        db.rollback()
        log.error("[Payment] atomic confirm failed for registration %s: %s", reg.id, e)
        if isinstance(e, BookingError):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        raise HTTPException(status_code=500, detail="Payment verified but ticket could not be created. Contact support.")
    t = out["ticket"]
    log.info("[Payment] PAYMENT_MARKED_COMPLETED registration=%s transaction=%s",
             reg.id, payment.transaction_id)
    log.info("[Registration] REGISTRATION_CONFIRMED registration=%s", reg.id)
    if t:
        log.info("[Ticket] TICKET_CREATED id=%s code=%s", t.id, t.ticket_code)
    else:
        log.info("[Ticket] TICKET_ALREADY_EXISTS registration=%s", reg.id)
    return {"success": True, "message": "Payment verified. Ticket issued.",
            "data": {"ticket_id": t.id if t else None, "ticket_code": t.ticket_code if t else None,
                     "qr_token": t.qr_token if t else None, "qr_code_url": t.qr_code_url if t else None,
                     "registration_id": reg.id}}


@api_router.get("/esewa/return")
def esewa_browser_return(data: str | None = None):
    """Backend success handler: eSewa may be pointed here; we log the return
    and bounce to the frontend callback (which carries auth and verifies)."""
    log.info("[eSewa] PAYMENT_RETURNED via backend handler")
    base = f"{settings.FRONTEND_URL.rstrip('/')}/payments/callback"
    qs = f"?provider=ESEWA&data={data}" if data else "?provider=ESEWA"
    return RedirectResponse(url=base + qs, status_code=307)


@api_router.get("/by-registration/{registration_id}", response_model=dict)
def payments_for_registration(registration_id: int, user: UserModel = Depends(require_auth),
                              db: Session = Depends(get_db)):
    reg = _own_pending(db, user, registration_id)
    rows = db.query(Payment).filter(Payment.registration_id == reg.id).order_by(Payment.created_at.desc()).all()
    return {"success": True, "items": [
        {"id": p.id, "provider": str(getattr(p.provider, "value", p.provider)),
         "transaction_id": p.transaction_id, "amount": p.amount,
         "status": str(getattr(p.status, "value", p.status)), "created_at": p.created_at}
        for p in rows]}


@api_router.get("/wallet", response_model=dict)
def my_wallet(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    """Organizer wallet preview (full dashboard in Phase 6)."""
    from app.models.organizer import OrganizerProfile

    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Organizer profile required")
    return {"success": True, "data": get_wallet_view(db, org.id)}
