"""Database models - imports all models to register with Base"""
from app.database import Base
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.models.event import Event, EventCategory
from app.models.organizer import OrganizerProfile
from app.models.event_image import EventImage
from app.models.ticket import TicketType, Registration, Ticket, TicketScan
from app.models.other import EventReview, Favorite, Notification, Report, AuditLog

# Ensure all models are imported for Base.metadata
__all__ = [
    "Base",
    "User", "Role", "Permission", "UserRole", "RolePermission",
    "Event", "EventCategory",
    "OrganizerProfile",
    "EventImage",
    "TicketType", "Registration", "Ticket", "TicketScan",
    "EventReview", "Favorite", "Notification", "Report", "AuditLog",
]