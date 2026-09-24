"""Search — Phase 3 (lifecycle-aware, never returns ended events)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import Event
from app.services.lifecycle import serialize_event

api_router = APIRouter(prefix="/search", tags=["Search"])


@api_router.get("/", response_model=dict)
def search_events(
    q: Optional[str] = Query(default=None),
    category: Optional[str] = None,
    city: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    from datetime import timedelta

    from app.models.event import EventCategory
    from app.services.lifecycle import PUBLIC_STATUSES

    q = (q or "").strip()
    if not q and not category and not city and not date_from and not date_to:
        return {"success": True, "items": [], "total": 0, "page": page,
                "per_page": per_page, "message": "Type a keyword or set a filter"}
    query = db.query(Event).filter(Event.status.in_(list(PUBLIC_STATUSES)))
    # hide ended (same predicate as discovery)
    now = datetime.utcnow()
    query = query.filter(
        ~or_(
            (Event.end_date.isnot(None)) & (Event.end_date <= now),
            (Event.end_date.is_(None)) & (Event.start_date <= now - timedelta(hours=4)),
        )
    )
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Event.title.ilike(like),
                Event.short_description.ilike(like),
                Event.city.ilike(like),
                Event.venue.ilike(like),
            )
        )
    if category:
        query = query.join(EventCategory, EventCategory.id == Event.category_id).filter(
            or_(EventCategory.name.ilike(f"%{category}%"), EventCategory.slug == category.lower())
        )
    if city:
        query = query.filter(Event.city.ilike(f"%{city}%"))
    if date_from:
        query = query.filter(or_(Event.end_date >= date_from, Event.start_date >= date_from))
    if date_to:
        query = query.filter(Event.start_date <= date_to)

    total = query.count()
    events = query.order_by(Event.start_date.asc()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "success": True,
        "items": [serialize_event(ev, db) for ev in events],
        "total": total, "page": page, "per_page": per_page,
        "message": "Search results",
    }
