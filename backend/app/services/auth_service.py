import qrcode
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import Base, engine
from app.models.user import User
from app.models.event import Event
from app.models.ticket import Registration, Ticket, TicketScan
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def generate_qr_token():
    return str(uuid.uuid4().hex)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def register_user(event_id: int, user_id: int, ticket_type_id: int, db: Session):
    from app.models.event import Event as EventModel
    from app.models.ticket import TicketType as TicketTypeModel

    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise ValueError("Event not found")

    ticket_type = db.query(TicketTypeModel).filter(TicketTypeModel.id == ticket_type_id).first()
    if not ticket_type:
        raise ValueError("Ticket type not found")

    if ticket_type.status != "ACTIVE":
        raise ValueError("Ticket type is not available")

    if ticket_type.sold_count >= ticket_type.capacity:
        raise ValueError("Ticket type is sold out")

    existing = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.user_id == user_id,
        Registration.ticket_type_id == ticket_type_id,
        Registration.status == "CONFIRMED",
    ).first()
    if existing:
        raise ValueError("User already registered for this event with this ticket type")

    event_capacity_used = db.query(func.count(Registration.id)).filter(
        Registration.event_id == event_id,
        Registration.status == "CONFIRMED",
    ).scalar() or 0
    if event_capacity_used >= event.max_capacity:
        raise ValueError("Event is at full capacity")

    from app.models.ticket import RegistrationStatus, PaymentStatus, Registration as RegistrationModel
    registration = RegistrationModel(
        event_id=event_id,
        user_id=user_id,
        ticket_type_id=ticket_type_id,
        status=RegistrationStatus.CONFIRMED,
        payment_status=PaymentStatus.UNPAID,
        amount_paid=0.0 if event.price_min == 0 else ticket_type.price,
    )
    db.add(registration)
    db.flush()

    ticket_type.sold_count += 1

    ticket_code = f"EV-{str(registration.id).zfill(6)}"
    qr_token = generate_qr_token()

    from app.models.ticket import Ticket as TicketModel, TicketStatusValid
    ticket = TicketModel(
        registration_id=registration.id,
        ticket_type_id=ticket_type_id,
        ticket_code=ticket_code,
        qr_token=qr_token,
        status=TicketStatusValid.VALID,
    )
    db.add(ticket)
    db.commit()
    db.refresh(registration)
    db.refresh(ticket)

    return registration, ticket


def check_in_ticket(qr_token: str, scanned_by_user_id: int, db: Session):
    ticket = db.query(Ticket).filter(Ticket.qr_token == qr_token).first()
    if not ticket:
        return {"valid": False, "error": "INVALID_TICKET", "message": "This ticket could not be verified."}

    if ticket.status == "USED":
        return {"valid": False, "error": "ALREADY_CHECKED_IN", "message": "This ticket was previously used."}

    if ticket.status == "CANCELLED":
        return {"valid": False, "error": "CANCELLED_TICKET", "message": "This ticket has been cancelled."}

    if ticket.status == "EXPIRED":
        return {"valid": False, "error": "EXPIRED_TICKET", "message": "This ticket has expired."}

    ticket.status = "USED"
    ticket.checked_in_at = datetime.utcnow()

    scan = TicketScan(
        ticket_id=ticket.id,
        scanned_by_user_id=scanned_by_user_id,
        result="SUCCESS",
    )
    db.add(scan)
    db.commit()
    db.refresh(ticket)

    return {
        "valid": True,
        "error": None,
        "message": "Checked in successfully",
        "ticket": {
            "id": ticket.id,
            "ticket_code": ticket.ticket_code,
            "registration_id": ticket.registration_id,
            "status": ticket.status,
            "checked_in_at": ticket.checked_in_at,
        },
    }
