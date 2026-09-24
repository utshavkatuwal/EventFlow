"""Registrations — Phase 4 (user orders: PENDING → CONFIRMED)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import rate_limit, require_admin, require_auth
from app.database import get_db
from app.models.event import Event
from app.models.ticket import Registration
from app.models.user import User as UserModel
from app.services.booking import BookingError, cancel_booking, create_booking
from app.services.lifecycle import compute_lifecycle, serialize_event

api_router = APIRouter(prefix="/registrations", tags=["Registrations"])


def _serialize(reg: Registration, db: Session) -> dict:
    from app.models.ticket import Ticket, TicketType

    ev = db.query(Event).filter(Event.id == reg.event_id).first()
    tt = db.query(TicketType).filter(TicketType.id == reg.ticket_type_id).first()
    ticket = db.query(Ticket).filter(Ticket.registration_id == reg.id).first()
    data = {
        "id": reg.id,
        "event_id": reg.event_id,
        "ticket_type_id": reg.ticket_type_id,
        "ticket_type_name": tt.name if tt else None,
        "status": str(getattr(reg.status, "value", reg.status)),
        "payment_status": str(getattr(reg.payment_status, "value", reg.payment_status)),
        "amount_paid": reg.amount_paid,
        "registration_date": reg.registration_date,
        "created_at": reg.created_at,
        "ticket_id": ticket.id if ticket else None,
        "ticket_code": ticket.ticket_code if ticket else None,
    }
    if ev:
        data["event"] = serialize_event(ev, db)
    return data


@api_router.post("", response_model=dict, dependencies=[Depends(rate_limit(60, 60))])
def create_registration(
    payload: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)
):
    try:
        out = create_booking(db, user, payload.get("event_id"), payload.get("ticket_type_id"))
    except BookingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    reg = out["registration"]
    if out["payment_required"]:
        return {
            "success": True,
            "message": "Order created. Complete payment to get your ticket.",
            "data": {
                "registration_id": reg.id,
                "payment_required": True,
                "amount": out["amount"],
                "registration": _serialize(reg, db),
            },
        }
    t = out["ticket"]
    return {
        "success": True,
        "message": "Registration successful. Ticket issued.",
        "data": {
            "registration_id": reg.id,
            "ticket_id": t.id,
            "ticket_code": t.ticket_code,
            "qr_token": t.qr_token,
            "qr_code_url": t.qr_code_url,
            "payment_required": False,
            "registration": _serialize(reg, db),
        },
    }


@api_router.get("/me", response_model=dict)
def my_registrations(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    regs = (
        db.query(Registration)
        .filter(Registration.user_id == user.id)
        .order_by(Registration.created_at.desc())
        .all()
    )
    return {"success": True, "items": [_serialize(r, db) for r in regs]}


@api_router.get("/{reg_id}", response_model=dict)
def get_registration(reg_id: int, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    from app.models.organizer import OrganizerProfile

    reg = db.query(Registration).filter(Registration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    if reg.user_id != user.id:
        # organizer of the event or admin may view
        ev = db.query(Event).filter(Event.id == reg.event_id).first()
        org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
        from app.auth.dependencies import get_user_roles

        is_admin = "admin" in get_user_roles(db, user.id)
        if not is_admin and (not org or not ev or ev.organizer_id != org.id):
            raise HTTPException(status_code=403, detail="Not your registration")
    return {"success": True, "data": _serialize(reg, db)}


@api_router.post("/{reg_id}/cancel", response_model=dict)
def cancel_registration(reg_id: int, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    from app.models.ticket import Ticket, TicketStatusValid

    reg = db.query(Registration).filter(Registration.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    if reg.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your registration")
    ticket = db.query(Ticket).filter(Ticket.registration_id == reg.id).first()
    if ticket and str(getattr(ticket.status, "value", ticket.status)) == "USED":
        raise HTTPException(status_code=400, detail="Used tickets cannot be cancelled")
    cancel_booking(db, reg)
    return {"success": True, "message": "Registration cancelled"}
