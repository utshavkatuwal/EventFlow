"""Event lifecycle + serialization (Phase 3).

Stored `status` (DRAFT/PUBLISHED/CANCELLED/...) is the organizer/admin workflow state.
Computed `lifecycle` (UPCOMING/ONGOING/ENDED) is derived from dates and never stored:

    NOW < start_at                -> UPCOMING
    start_at <= NOW < end_at      -> ONGOING
    NOW >= end_at                 -> ENDED

Ended events are NEVER deleted — they are hidden from public discovery queries
but remain visible in user/organizer history.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

# Events without an end date are treated as 4-hour programs for lifecycle purposes.
DEFAULT_DURATION = timedelta(hours=4)

PUBLIC_STATUSES = ("APPROVED", "PUBLISHED")


def effective_end(start, end) -> Optional[datetime]:
    if end:
        return end
    if start:
        return start + DEFAULT_DURATION
    return None


def compute_lifecycle(start, end, now: Optional[datetime] = None) -> str:
    now = now or datetime.utcnow()
    if not start:
        return "UPCOMING"
    end_eff = effective_end(start, end)
    if now < start:
        return "UPCOMING"
    if end_eff and now < end_eff:
        return "ONGOING"
    if not end_eff:
        return "ONGOING"
    return "ENDED"


def is_publicly_available(event, now: Optional[datetime] = None) -> bool:
    """Public discovery predicate: published workflow state + not ended/cancelled."""
    if getattr(event, "status", None) in ("CANCELLED", "REJECTED", "DRAFT", "PENDING_REVIEW"):
        # stored status may be str or Enum
        status = str(getattr(event.status, "value", event.status))
        if status in ("CANCELLED", "REJECTED", "DRAFT", "PENDING_REVIEW"):
            return False
    status = str(getattr(event.status, "value", getattr(event, "status", "")))
    if status not in PUBLIC_STATUSES:
        return False
    return compute_lifecycle(event.start_date, event.end_date, now) != "ENDED"


def serialize_event(ev, db, include_ticket_types: bool = False) -> dict:
    """Full card/detail payload including lifecycle + capacity (no lazy-load traps)."""
    from sqlalchemy import func

    from app.models.event import EventCategory
    from app.models.organizer import OrganizerProfile
    from app.models.ticket import Registration, TicketType

    organizer = (
        db.query(OrganizerProfile).filter(OrganizerProfile.id == ev.organizer_id).first()
    )
    category = (
        db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
    )
    reg_count = (
        db.query(func.count(Registration.id))
        .filter(Registration.event_id == ev.id, Registration.status == "CONFIRMED")
        .scalar()
        or 0
    )
    data = {
        "id": ev.id,
        "organizer_id": ev.organizer_id,
        "category_id": ev.category_id,
        "title": ev.title,
        "slug": ev.slug,
        "short_description": ev.short_description,
        "full_description": getattr(ev, "full_description", None),
        "cover_image_url": ev.cover_image_url,
        "video_url": getattr(ev, "video_url", None),
        "venue": ev.venue,
        "address": ev.address,
        "city": ev.city,
        "country": ev.country,
        "start_date": ev.start_date,
        "end_date": ev.end_date,
        "max_capacity": ev.max_capacity,
        "status": str(getattr(ev.status, "value", ev.status)),
        "lifecycle": compute_lifecycle(ev.start_date, ev.end_date),
        "is_featured": ev.is_featured,
        "price_min": ev.price_min,
        "organizer_name": organizer.organization_name if organizer else None,
        "category_name": category.name if category else None,
        "total_registrations": reg_count,
        "available_capacity": max(ev.max_capacity - reg_count, 0),
        "created_at": ev.created_at,
        "updated_at": ev.updated_at,
    }
    if include_ticket_types:
        tts = db.query(TicketType).filter(TicketType.event_id == ev.id).all()
        data["ticket_types"] = [
            {
                "id": t.id,
                "name": t.name,
                "price": t.price,
                "capacity": t.capacity,
                "sold_count": t.sold_count,
                "status": str(getattr(t.status, "value", t.status)),
            }
            for t in tts
        ]
    return data
