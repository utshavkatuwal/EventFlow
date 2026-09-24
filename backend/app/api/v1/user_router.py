"""User self-service — Phase 4 (central auth, lifecycle-aware history).

Canonical paths used by the frontend dashboard:
  GET /user/stats|upcoming|past|saved|reviews  GET|PATCH /user/me
(Event detail variants also exist under events_router; both stay working.)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_roles, require_auth
from app.database import get_db
from app.models.event import Event, EventCategory
from app.models.organizer import OrganizerProfile
from app.models.other import Favorite
from app.models.ticket import Registration
from app.models.user import User as UserModel
from app.services.lifecycle import compute_lifecycle, serialize_event

api_router = APIRouter(prefix="/user", tags=["User"])


@api_router.get("/stats", response_model=dict)
def user_stats(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    total = db.query(func.count(Registration.id)).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").scalar() or 0
    regs = db.query(Registration).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    upcoming = 0
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        if ev and compute_lifecycle(ev.start_date, ev.end_date) == "UPCOMING":
            upcoming += 1
    saved = db.query(func.count(Favorite.id)).filter(Favorite.user_id == user.id).scalar() or 0
    return {"success": True, "data": {"total_registrations": total, "upcoming": upcoming, "saved": saved}}


@api_router.get("/upcoming", response_model=dict)
def user_upcoming(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    regs = db.query(Registration).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    result = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        if ev and compute_lifecycle(ev.start_date, ev.end_date) == "UPCOMING":
            result.append(serialize_event(ev, db))
    return {"success": True, "items": result}


@api_router.get("/past", response_model=dict)
def user_past(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    regs = db.query(Registration).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    result = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        if ev and compute_lifecycle(ev.start_date, ev.end_date) == "ENDED":
            result.append(serialize_event(ev, db))
    return {"success": True, "items": result}


@api_router.get("/saved", response_model=dict)
def user_saved(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    favs = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    ids = [f.event_id for f in favs]
    if not ids:
        return {"success": True, "items": []}
    return {"success": True, "items": [serialize_event(ev, db) for ev in db.query(Event).filter(Event.id.in_(ids)).all()]}


@api_router.get("/reviews", response_model=dict)
def user_reviews(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    from app.models.other import EventReview

    rows = db.query(EventReview).filter(EventReview.user_id == user.id).order_by(EventReview.created_at.desc()).all()
    return {"success": True, "items": [
        {"id": r.id, "event_id": r.event_id, "rating": r.rating, "comment": r.comment,
         "created_at": r.created_at, "updated_at": r.updated_at} for r in rows]}


@api_router.get("/me", response_model=dict)
def get_me(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    return {
        "success": True,
        "data": {
            "id": user.id, "email": user.email, "username": user.username,
            "first_name": user.first_name, "last_name": user.last_name,
            "phone": user.phone, "avatar_url": user.avatar_url,
            "is_active": user.is_active, "is_email_verified": user.is_email_verified,
            "account_type": getattr(user, "account_type", "USER") or "USER",
            "roles": get_user_roles(db, user.id),
            "role": "organizer" if org else "user",
            "created_at": user.created_at, "updated_at": user.updated_at,
        },
        "message": "User info retrieved",
    }


@api_router.patch("/me", response_model=dict)
def update_me(payload: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    for field in ["first_name", "last_name", "phone", "avatar_url"]:
        if field in payload:
            setattr(user, field, payload[field])
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Profile updated",
            "data": {"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "phone": user.phone}}
