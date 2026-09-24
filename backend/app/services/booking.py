"""Booking engine — Phase 4 (PENDING → CONFIRMED → ticket + QR).

Flow:
    User → create_booking() → PENDING registration
      free event  → confirmed immediately → ticket + QR issued
      paid event  → stays PENDING → Phase 5 payment verifies → confirm_booking()

All capacity checks run inside ONE transaction with SELECT … FOR UPDATE on the
ticket-type row, so concurrent checkouts cannot oversell. Duplicate protection
via the (event, user, ticket_type) unique constraint → IntegrityError → 409.
Ended/cancelled events and closed sales windows are rejected.
"""
from __future__ import annotations

import io
import secrets
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings

TICKET_QR_DIR = "uploads/tickets"


class BookingError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _get_event(db: Session, event_id: int):
    from app.models.event import Event

    try:
        event_id = int(event_id)
    except (TypeError, ValueError):
        raise BookingError("Invalid event_id", 400)
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise BookingError("Event not found", 404)
    return ev


def _ensure_sale_open(ev) -> None:
    from app.services.lifecycle import compute_lifecycle

    status = str(getattr(ev.status, "value", ev.status))
    if status == "CANCELLED":
        raise BookingError("Event was cancelled. New purchases are closed.", 400)
    if status not in ("PUBLISHED", "APPROVED"):
        raise BookingError("Event is not on sale.", 400)
    if compute_lifecycle(ev.start_date, ev.end_date) == "ENDED":
        raise BookingError("Event has ended. New purchases are closed.", 400)


def _lock_ticket_type(db: Session, event_id: int, ticket_type_id: int):
    from app.models.ticket import TicketType

    if ticket_type_id is None:
        raise BookingError("Select a ticket type", 400)
    try:
        ticket_type_id = int(ticket_type_id)
    except (TypeError, ValueError):
        raise BookingError("Invalid ticket_type_id", 400)
    tt = (
        db.query(TicketType)
        .filter(TicketType.id == ticket_type_id, TicketType.event_id == event_id)
        .with_for_update()
        .first()
    )
    if not tt:
        raise BookingError("Ticket type not found for this event", 404)
    if str(getattr(tt.status, "value", tt.status)) != "ACTIVE":
        raise BookingError("Ticket type is not on sale", 400)
    now = datetime.utcnow()
    if tt.sale_start and now < tt.sale_start:
        raise BookingError("Ticket sales have not started", 400)
    if tt.sale_end and now > tt.sale_end:
        raise BookingError("Ticket sales have ended", 400)
    if (tt.sold_count or 0) >= (tt.capacity or 0):
        raise BookingError("Ticket type is sold out", 400)
    return tt


def _check_event_capacity(db: Session, ev) -> None:
    from sqlalchemy import func

    from app.models.ticket import Registration

    used = (
        db.query(func.count(Registration.id))
        .filter(Registration.event_id == ev.id, Registration.status == "CONFIRMED")
        .scalar()
        or 0
    )
    if used >= (ev.max_capacity or 0):
        raise BookingError("Event is at full capacity", 400)


def _write_qr_png(qr_token: str, ticket_code: str) -> str:
    """QR contains ONLY the opaque token — no user/event PII."""
    import qrcode

    dest = Path(TICKET_QR_DIR)
    dest.mkdir(parents=True, exist_ok=True)
    img = qrcode.make(qr_token)
    path = dest / f"{ticket_code}.png"
    img.save(str(path))
    return f"/uploads/tickets/{ticket_code}.png"


def issue_ticket(db: Session, registration):
    """Create the unique ticket for a CONFIRMED registration (idempotent).

    A rebooked (revived) order gets a FRESH ticket — the old CANCELLED row
    stays for audit, so we only reuse a still-VALID ticket.
    """
    from app.models.ticket import Ticket, TicketStatusValid

    existing = (
        db.query(Ticket)
        .filter(
            Ticket.registration_id == registration.id,
            Ticket.status == TicketStatusValid.VALID,
        )
        .first()
    )
    if existing:
        return existing
    for _ in range(5):
        code = f"EV-{uuid.uuid4().hex[:6].upper()}"
        if not db.query(Ticket).filter(Ticket.ticket_code == code).first():
            break
    token = secrets.token_urlsafe(32)
    while db.query(Ticket).filter(Ticket.qr_token == token).first():
        token = secrets.token_urlsafe(32)
    ticket = Ticket(
        registration_id=registration.id,
        ticket_type_id=registration.ticket_type_id,
        ticket_code=code,
        qr_token=token,
        qr_code_url=_write_qr_png(token, code),
        status=TicketStatusValid.VALID,
    )
    db.add(ticket)
    db.flush()
    return ticket


def create_booking(db: Session, user, event_id: int, ticket_type_id: int) -> dict:
    """Create a PENDING order; free events confirm + issue ticket immediately."""
    from sqlalchemy import func

    from app.models.ticket import PaymentStatus, Registration, RegistrationStatus

    ev = _get_event(db, event_id)
    _ensure_sale_open(ev)
    # Duplicate guard (friendly 409 before hitting the unique constraint).
    dup = (
        db.query(Registration)
        .filter(
            Registration.event_id == ev.id,
            Registration.user_id == user.id,
            Registration.ticket_type_id == int(ticket_type_id),
            Registration.status.in_(["PENDING", "CONFIRMED"]),
        )
        .first()
    )
    if dup:
        raise BookingError("You already have a ticket order for this ticket type", 409)

    tt = _lock_ticket_type(db, ev.id, ticket_type_id)
    _check_event_capacity(db, ev)

    price = float(tt.price or 0.0)
    # Revive a previously-cancelled order (unique constraint covers all
    # statuses, so reuse the row instead of inserting a duplicate).
    cancelled = (
        db.query(Registration)
        .filter(
            Registration.event_id == ev.id,
            Registration.user_id == user.id,
            Registration.ticket_type_id == int(ticket_type_id),
            Registration.status == "CANCELLED",
        )
        .first()
    )
    if cancelled:
        cancelled.status = RegistrationStatus.PENDING
        cancelled.payment_status = PaymentStatus.UNPAID
        cancelled.amount_paid = 0.0
        registration = cancelled
        db.flush()
    else:
        registration = Registration(
            event_id=ev.id,
            user_id=user.id,
            ticket_type_id=tt.id,
            status=RegistrationStatus.PENDING,
            payment_status=PaymentStatus.UNPAID,
            amount_paid=0.0,
        )
        db.add(registration)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            raise BookingError("You already have a ticket order for this ticket type", 409)

    if price <= 0:
        # Free: confirm + ticket now (atomic with the capacity checks above).
        registration.status = RegistrationStatus.CONFIRMED
        registration.payment_status = PaymentStatus.PAID
        tt.sold_count = (tt.sold_count or 0) + 1
        ticket = issue_ticket(db, registration)
        db.commit()
        db.refresh(registration)
        return {"registration": registration, "ticket": ticket, "payment_required": False}

    db.commit()
    db.refresh(registration)
    return {"registration": registration, "ticket": None, "payment_required": True, "amount": price}


def confirm_booking(db: Session, registration, amount: float, commit: bool = True):
    """Confirm a PENDING order after verified payment (idempotent — Phase 5)."""
    from app.models.ticket import PaymentStatus, RegistrationStatus, TicketType

    db.refresh(registration)
    if str(getattr(registration.status, "value", registration.status)) == "CONFIRMED":
        from app.models.ticket import Ticket

        ticket = db.query(Ticket).filter(Ticket.registration_id == registration.id).first()
        return {"registration": registration, "ticket": ticket, "already": True}
    tt = (
        db.query(TicketType)
        .filter(TicketType.id == registration.ticket_type_id)
        .with_for_update()
        .first()
    )
    if (tt.sold_count or 0) >= (tt.capacity or 0):
        raise BookingError("Ticket type just sold out", 409)
    registration.status = RegistrationStatus.CONFIRMED
    registration.payment_status = PaymentStatus.PAID
    registration.amount_paid = amount
    tt.sold_count = (tt.sold_count or 0) + 1
    ticket = issue_ticket(db, registration)
    if commit:
        db.commit()
    else:
        db.flush()
    db.refresh(registration)
    return {"registration": registration, "ticket": ticket, "already": False}


def cancel_booking(db: Session, registration, by_admin: bool = False) -> None:
    """Cancel an order; frees capacity. Paid refunds handled in Phase 7."""
    from app.models.ticket import RegistrationStatus, Ticket, TicketStatusValid, TicketType

    if str(getattr(registration.status, "value", registration.status)) == "CANCELLED":
        return
    was_confirmed = str(getattr(registration.status, "value", registration.status)) == "CONFIRMED"
    registration.status = RegistrationStatus.CANCELLED
    ticket = db.query(Ticket).filter(Ticket.registration_id == registration.id).first()
    if ticket and str(getattr(ticket.status, "value", ticket.status)) == "VALID":
        ticket.status = TicketStatusValid.CANCELLED
    if was_confirmed:
        tt = (
            db.query(TicketType)
            .filter(TicketType.id == registration.ticket_type_id)
            .with_for_update()
            .first()
        )
        if tt and (tt.sold_count or 0) > 0:
            tt.sold_count -= 1
    db.commit()


def to_http_error(e: BookingError) -> HTTPException:
    return HTTPException(status_code=e.status_code, detail=str(e))
