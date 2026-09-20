import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.ticket import Ticket
from app.core.security import verify_token
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/tickets", tags=["Tickets"])


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not token:
        return None
    from app.core.security import verify_token as vt
    payload = vt(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


@api_router.get("/{ticket_id}", response_model=dict)
def get_ticket(ticket_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    reg = db.query(db.query(UserModel).join(Ticket).filter(Ticket.id == ticket_id).first())
    from app.models.ticket import Registration as RegistrationModel
    registration = db.query(RegistrationModel).filter(RegistrationModel.id == ticket.registration_id).first()
    event = db.query(db.query(UserModel).join(Ticket).filter(Ticket.id == ticket_id).first())
    from app.models.event import Event as EventModel
    event = db.query(EventModel).filter(EventModel.id == registration.event_id).first() if registration else None
    from app.models.ticket import TicketType as TicketTypeModel
    ticket_type = db.query(TicketTypeModel).filter(TicketTypeModel.id == ticket.ticket_type_id).first()
    from app.models.other import OrganizerProfile
    organizer = db.query(OrganizerProfile).filter(OrganizerProfile.id == event.organizer_id).first() if event else None
    from app.models.event_category import EventCategory
    category = db.query(EventCategory).filter(EventCategory.id == event.category_id).first() if event else None
    
    return {
        "success": True,
        "data": {
            "id": ticket.id,
            "registration_id": ticket.registration_id,
            "ticket_type_id": ticket.ticket_type_id,
            "ticket_code": ticket.ticket_code,
            "qr_token": ticket.qr_token,
            "qr_code_url": ticket.qr_code_url,
            "status": ticket.status,
            "checked_in_at": ticket.checked_in_at,
            "created_at": ticket.created_at,
            "event_title": event.title if event else None,
            "event_date": event.start_date if event else None,
            "event_location": event.venue if event else None,
            "ticket_type_name": ticket_type.name if ticket_type else None,
            "attendee_name": f"{user.first_name} {user.last_name}".strip() if user else user.username,
        },
        "message": "Ticket retrieved"
    }


@api_router.get("/my", response_model=dict)
def get_my_tickets(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.models.ticket import Registration as RegistrationModel
    regs = db.query(RegistrationModel).filter(RegistrationModel.user_id == user.id).all()
    reg_ids = [r.id for r in regs]
    
    from app.models.ticket import Ticket as TicketModel
    tickets = db.query(TicketModel).filter(TicketModel.registration_id.in_(reg_ids)).all()
    
    result = []
    for t in tickets:
        from app.models.event import Event as EventModel
        reg = db.query(RegistrationModel).filter(RegistrationModel.id == t.registration_id).first()
        event = db.query(EventModel).filter(EventModel.id == reg.event_id).first() if reg else None
        from app.models.ticket import TicketType as TicketTypeModel
        tt = db.query(TicketTypeModel).filter(TicketTypeModel.id == t.ticket_type_id).first()
        result.append({
            "id": t.id,
            "ticket_code": t.ticket_code,
            "qr_token": t.qr_token,
            "status": t.status,
            "checked_in_at": t.checked_in_at,
            "event_title": event.title if event else "Unknown",
            "event_date": event.start_date if event else None,
            "event_location": event.venue if event else None,
            "ticket_type_name": tt.name if tt else None,
        })
    
    return {"success": True, "items": result, "message": "Tickets retrieved"}