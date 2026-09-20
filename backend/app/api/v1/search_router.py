from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.event import Event, EventCategory
from app.models.ticket import Registration, TicketType, Ticket
from app.core.security import verify_token
from app.core.config import settings
from sqlalchemy import func, desc
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/search", tags=["Search"])


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


from app.models.user import User as UserModel


@api_router.get("/", response_model=dict)
def search_events(
    q: str = Query(..., min_length=1),
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
):
    search = f"%{q}%"
    
    events = db.query(Event).filter(
        Event.title.ilike(search) |
        Event.short_description.ilike(search) |
        Event.city.ilike(search) |
        Event.venue.ilike(search)
    ).all()
    
    result_items = []
    for ev in events:
        cat = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
        org = db.query(db.query(UserModel).join(Event).filter(Event.id == ev.id).first())
        from app.models.other import OrganizerProfile
        organizer = db.query(OrganizerProfile).filter(OrganizerProfile.id == ev.organizer_id).first()
        reg_count = db.query(func.count(Registration.id)).filter(Registration.event_id == ev.id, Registration.status == "CONFIRMED").scalar() or 0
        result_items.append({
            "id": ev.id,
            "title": ev.title,
            "slug": ev.slug,
            "short_description": ev.short_description,
            "cover_image_url": ev.cover_image_url,
            "city": ev.city,
            "venue": ev.venue,
            "category_name": cat.name if cat else None,
            "organizer_name": organizer.organization_name if organizer else None,
            "start_date": ev.start_date,
            "price_min": ev.price_min,
            "status": ev.status,
            "total_registrations": reg_count,
            "available_capacity": ev.max_capacity - reg_count,
        })
    
    return {
        "success": True,
        "items": result_items,
        "total": len(result_items),
        "page": page,
        "per_page": per_page,
        "message": "Search results"
    }
