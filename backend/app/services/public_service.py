from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.event import Event
from app.models.ticket import Registration, Ticket, TicketType
from datetime import datetime


def get_event_stats(db: Session = None):
    if db is None:
        db = SessionLocal()
    try:
        now = datetime.utcnow()
        total = db.query(Event).count()
        upcoming = db.query(Event).filter(
            Event.start_date >= now,
            Event.status.in_(["APPROVED", "PUBLISHED"]),
        ).count()
        published = db.query(Event).filter(
            Event.status.in_(["APPROVED", "PUBLISHED"]),
        ).count()
        total_registrations = db.query(Registration).filter(
            Registration.status == "CONFIRMED",
        ).count()
        return {
            "total_events": total,
            "upcoming_events": upcoming,
            "published_events": published,
            "total_registrations": total_registrations,
        }
    finally:
        if db is None:
            db.close()
