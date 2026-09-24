"""Tickets — Phase 4 (central auth, owner/organizer/admin visibility)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_roles, require_auth
from app.database import get_db
from app.models.event import Event
from app.models.organizer import OrganizerProfile
from app.models.ticket import Ticket
from app.models.user import User as UserModel
from app.services.lifecycle import serialize_event

api_router = APIRouter(prefix="/tickets", tags=["Tickets"])


def _serialize_ticket(t: Ticket, db: Session, viewer: UserModel) -> dict:
    from app.models.ticket import Registration as RegistrationModel
    from app.models.ticket import TicketType as TicketTypeModel

    reg = db.query(RegistrationModel).filter(RegistrationModel.id == t.registration_id).first()
    event = db.query(Event).filter(Event.id == reg.event_id).first() if reg else None
    tt = db.query(TicketTypeModel).filter(TicketTypeModel.id == t.ticket_type_id).first()
    attendee = db.query(UserModel).filter(UserModel.id == reg.user_id).first() if reg else None
    data = {
        "id": t.id,
        "registration_id": t.registration_id,
        "ticket_type_id": t.ticket_type_id,
        "ticket_code": t.ticket_code,
        "qr_token": t.qr_token,
        "qr_code_url": t.qr_code_url,
        "status": str(getattr(t.status, "value", t.status)),
        "checked_in_at": t.checked_in_at,
        "created_at": t.created_at,
        "event_title": event.title if event else "Unknown",
        "event_date": event.start_date if event else None,
        "event_location": (event.venue if event else None) or (event.city if event else None),
        "ticket_type_name": tt.name if tt else None,
        "attendee_name": (
            f"{attendee.first_name or ''} {attendee.last_name or ''}".strip() or (attendee.username if attendee else None)
        ),
        "payment_status": str(getattr(reg.payment_status, "value", reg.payment_status)) if reg else None,
        "registration_status": str(getattr(reg.status, "value", reg.status)) if reg else None,
    }
    if event:
        data["lifecycle"] = serialize_event(event, db)["lifecycle"]
    return data


def _visible(ticket: Ticket, viewer: UserModel, db: Session) -> bool:
    from app.models.ticket import Registration as RegistrationModel

    reg = db.query(RegistrationModel).filter(RegistrationModel.id == ticket.registration_id).first()
    if not reg:
        return False
    if reg.user_id == viewer.id:
        return True
    if "admin" in get_user_roles(db, viewer.id):
        return True
    ev = db.query(Event).filter(Event.id == reg.event_id).first()
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == viewer.id).first()
    return bool(org and ev and ev.organizer_id == org.id)


# Static routes before /{ticket_id} (else "my" 422s on int parsing).
@api_router.get("/my", response_model=dict)
def get_my_tickets(viewer: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    from app.models.ticket import Registration as RegistrationModel

    regs = db.query(RegistrationModel).filter(RegistrationModel.user_id == viewer.id).all()
    ids = [r.id for r in regs]
    if not ids:
        return {"success": True, "items": [], "message": "Tickets retrieved"}
    tickets = db.query(Ticket).filter(Ticket.registration_id.in_(ids)).order_by(Ticket.created_at.desc()).all()
    return {"success": True, "items": [_serialize_ticket(t, db, viewer) for t in tickets], "message": "Tickets retrieved"}


@api_router.get("/{ticket_id}", response_model=dict)
def get_ticket(ticket_id: int, viewer: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if not _visible(ticket, viewer, db):
        raise HTTPException(status_code=403, detail="Not your ticket")
    return {"success": True, "data": _serialize_ticket(ticket, db, viewer), "message": "Ticket retrieved"}
