from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.event import Event
from app.models.ticket import Registration, Ticket
from app.models.other import EventReview, Notification
from app.models.user import User
from app.models.organizer import OrganizerProfile


def get_dashboard_stats_organizer(organizer_id: int, db: Session = None):
    if db is None:
        db = SessionLocal()
    try:
        total_events = db.query(Event).filter(Event.organizer_id == organizer_id).count()
        published_events = db.query(Event).filter(
            Event.organizer_id == organizer_id,
            Event.status.in_(["APPROVED", "PUBLISHED"]),
        ).count()
        total_registrations = db.query(Registration).join(Event).filter(
            Event.organizer_id == organizer_id,
            Registration.status == "CONFIRMED",
        ).count()
        total_attendees = db.query(Registration).join(Ticket).filter(
            Ticket.status == "USED",
            Registration.status == "CONFIRMED",
        ).join(Event).filter(Event.organizer_id == organizer_id).count()
        upcoming_events = db.query(Event).filter(
            Event.organizer_id == organizer_id,
            Event.status.in_(["APPROVED", "PUBLISHED"]),
            Event.start_date >= datetime.utcnow(),
        ).count()
        total_tickets_scanned = db.query(Ticket).join(Registration).join(Event).filter(
            Event.organizer_id == organizer_id,
            Ticket.status == "USED",
        ).count()
        total_tickets = db.query(Ticket).join(Registration).join(Event).filter(
            Event.organizer_id == organizer_id,
        ).count()
        checkin_percentage = (total_tickets_scanned / total_tickets * 100) if total_tickets > 0 else 0

        return {
            "total_events": total_events,
            "published_events": published_events,
            "total_registrations": total_registrations,
            "total_attendees": total_attendees,
            "upcoming_events": upcoming_events,
            "checkin_percentage": round(checkin_percentage, 1),
        }
    finally:
        if db is None:
            db.close()


def get_admin_stats(db: Session = None):
    if db is None:
        db = SessionLocal()
    try:
        total_users = db.query(User).filter(User.is_active == True).count()
        total_organizers = db.query(OrganizerProfile).count()
        total_events = db.query(Event).count()
        published_events = db.query(Event).filter(Event.status.in_(["APPROVED", "PUBLISHED"])).count()
        pending_events = db.query(Event).filter(Event.status == "PENDING_REVIEW").count()
        total_registrations = db.query(Registration).filter(Registration.status == "CONFIRMED").count()
        total_attendees = db.query(Ticket).filter(Ticket.status == "USED").count()
        total_reviews = db.query(EventReview).count()
        open_reports = db.query(Report).filter(Report.status == "OPEN").count()
        return {
            "total_users": total_users,
            "total_organizers": total_organizers,
            "total_events": total_events,
            "published_events": published_events,
            "pending_events": pending_events,
            "total_registrations": total_registrations,
            "total_attendees": total_attendees,
            "total_reviews": total_reviews,
            "open_reports": open_reports,
        }
    finally:
        if db is None:
            db.close()
