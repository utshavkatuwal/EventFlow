"""Events domain — Phase 3 (discovery + lifecycle + approved-organizer CRUD).

Public discovery NEVER returns ended/cancelled events (lifecycle computed in
`app.services.lifecycle`, never stored, never deleted).
Management (create/edit/publish/cancel) requires an APPROVED organizer and
ownership (or admin). DELETE is a soft-cancel to preserve history + ledger.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    require_admin,
    require_approved_organizer,
    require_auth,
    require_organizer_profile,
)
from app.database import get_db
from app.models.event import Event, EventCategory
from app.models.organizer import OrganizerProfile
from app.models.other import AuditLog, Favorite
from app.models.ticket import Registration, TicketType
from app.models.user import User as UserModel
from app.services.analytics_service import get_admin_stats, get_dashboard_stats_organizer
from app.services.auth_service import check_in_ticket, register_user
from app.services.lifecycle import (
    PUBLIC_STATUSES,
    compute_lifecycle,
    effective_end,
    serialize_event,
)
from app.services.public_service import get_event_stats

api_router = APIRouter()


# ---------- shared query helpers ----------
def _public_base(db: Session):
    """Workflow-state filter for public discovery (lifecycle applied in Python)."""
    return db.query(Event).filter(Event.status.in_(list(PUBLIC_STATUSES)))


def _ended_clause(now: datetime):
    """SQL predicate matching compute_lifecycle() == ENDED (DB-agnostic)."""
    return or_(
        and_(Event.end_date.isnot(None), Event.end_date <= now),
        and_(Event.end_date.is_(None), Event.start_date <= now - timedelta(hours=4)),
    )


def _apply_discovery_filters(query, *, category_id=None, q=None, city=None,
                             date_from=None, date_to=None, price=None, featured=None,
                             include_ended=False):
    if category_id:
        query = query.filter(Event.category_id == category_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Event.title.ilike(like),
                Event.short_description.ilike(like),
                Event.venue.ilike(like),
                Event.city.ilike(like),
            )
        )
    if city:
        query = query.filter(Event.city.ilike(f"%{city}%"))
    if date_from:
        query = query.filter(or_(Event.end_date >= date_from, Event.start_date >= date_from))
    if date_to:
        query = query.filter(Event.start_date <= date_to)
    if price == "free":
        query = query.filter((Event.price_min.is_(None)) | (Event.price_min <= 0))
    elif price == "paid":
        query = query.filter(Event.price_min > 0)
    if featured is not None:
        query = query.filter(Event.is_featured.is_(featured))
    if not include_ended:
        query = query.filter(~_ended_clause(datetime.utcnow()))
    return query


def _paginate_with_lifecycle(query, db: Session, *, page: int, per_page: int, sort: str):
    """Sort popular in SQL, paginate with a buffer, finalize lifecycle in Python."""
    if sort == "newest":
        query = query.order_by(Event.created_at.desc())
    elif sort == "popular":
        counts = (
            db.query(Registration.event_id, func.count(Registration.id).label("c"))
            .filter(Registration.status == "CONFIRMED")
            .group_by(Registration.event_id)
            .subquery()
        )
        query = query.outerjoin(counts, counts.c.event_id == Event.id).order_by(
            desc(func.coalesce(counts.c.c, 0)), Event.start_date.asc()
        )
    else:
        query = query.order_by(Event.start_date.asc())
    # Buffer over-fetch so lifecycle filtering keeps pages full at small scale.
    raw = query.offset(max(page - 1, 0) * per_page).limit(per_page * 3).all()
    items = [serialize_event(ev, db) for ev in raw]
    # Defensive: drop anything that slipped through (cancelled/ended).
    items = [i for i in items if i["lifecycle"] != "ENDED" and i["status"] != "CANCELLED"]
    return items[:per_page]


# ---------- root / health (legacy paths kept) ----------
@api_router.get("/", tags=["Root"])
def root():
    return {"success": True, "message": "EventFlow API v1"}


@api_router.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ---------- public discovery ----------
@api_router.get("/events", tags=["Events"])
def list_events(
    page: int = 1,
    per_page: int = 20,
    category_id: Optional[int] = None,
    q: Optional[str] = Query(default=None, description="Keyword across title/desc/venue/city"),
    search: Optional[str] = None,  # legacy alias
    city: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    price: Optional[str] = Query(default=None, description="free | paid"),
    featured: Optional[bool] = None,
    sort: str = "start_date",
    include_ended: bool = False,
    db: Session = Depends(get_db),
):
    keyword = q or search
    query = _apply_discovery_filters(
        _public_base(db),
        category_id=category_id, q=keyword, city=city,
        date_from=date_from, date_to=date_to, price=price,
        featured=featured, include_ended=include_ended,
    )
    total = query.count()
    items = _paginate_with_lifecycle(query, db, page=page, per_page=per_page, sort=sort)
    return {
        "success": True, "items": items, "total": total, "page": page,
        "per_page": per_page, "total_pages": (total + per_page - 1) // per_page,
        "message": "Events retrieved successfully",
    }


@api_router.get("/events/featured", tags=["Events"])
def featured_events(per_page: int = 6, db: Session = Depends(get_db)):
    query = _apply_discovery_filters(_public_base(db), featured=True)
    return {"success": True, "items": _paginate_with_lifecycle(query, db, page=1, per_page=per_page, sort="start_date")}


@api_router.get("/events/upcoming", tags=["Events"])
def upcoming_events(per_page: int = 20, page: int = 1, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    query = _public_base(db).filter(Event.start_date > now)
    query = _apply_discovery_filters(query)
    return {"success": True, "items": _paginate_with_lifecycle(query, db, page=page, per_page=per_page, sort="start_date")}


@api_router.get("/events/popular", tags=["Events"])
def popular_events(per_page: int = 10, db: Session = Depends(get_db)):
    query = _apply_discovery_filters(_public_base(db))
    return {"success": True, "items": _paginate_with_lifecycle(query, db, page=1, per_page=per_page, sort="popular")}


@api_router.get("/events/stats", tags=["Events"])
def event_stats(db: Session = Depends(get_db)):
    return {"success": True, "data": get_event_stats(db), "message": "Stats retrieved"}


@api_router.get("/events/{event_id}", tags=["Events"])
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True, "data": serialize_event(ev, db, include_ticket_types=True), "message": "Event retrieved successfully"}


@api_router.get("/events/{event_id}/tickets", tags=["Events"])
def get_event_tickets(event_id: int, db: Session = Depends(get_db)):
    if not db.query(Event).filter(Event.id == event_id).first():
        raise HTTPException(status_code=404, detail="Event not found")
    tickets = db.query(TicketType).filter(TicketType.event_id == event_id).all()
    return {"success": True, "items": [
        {"id": t.id, "event_id": t.event_id, "name": t.name, "description": t.description,
         "price": t.price, "currency": t.currency, "capacity": t.capacity,
         "sold_count": t.sold_count, "status": str(getattr(t.status, "value", t.status)),
         "created_at": t.created_at, "updated_at": t.updated_at}
        for t in tickets], "message": "Tickets retrieved"}


# ---------- organizer media upload (covers + videos, validated) ----------
MEDIA_RULES = {
    "cover": ({"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"},
              {".jpg", ".jpeg", ".png", ".webp"}, 10 * 1024 * 1024),
    "video": ({"video/mp4": ".mp4", "video/webm": ".webm", "video/quicktime": ".mov"},
              {".mp4", ".webm", ".mov"}, 100 * 1024 * 1024),
}


@api_router.post("/events/upload", tags=["Events"])
async def upload_event_media(
    file: UploadFile = File(...),
    kind: str = Query(default="cover", description="cover | video"),
    org: OrganizerProfile = Depends(require_organizer_profile),
    db: Session = Depends(get_db),
):
    from pathlib import Path

    if kind not in MEDIA_RULES:
        raise HTTPException(status_code=400, detail="kind must be cover or video")
    allowed_mime, allowed_ext, max_bytes = MEDIA_RULES[kind]
    ctype = (file.content_type or "").lower()
    if ctype not in allowed_mime:
        raise HTTPException(status_code=400, detail=f"Only {', '.join(sorted(allowed_ext))} allowed for {kind}")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="File type not allowed")
    blob = await file.read()
    if not blob or len(blob) > max_bytes:
        raise HTTPException(status_code=400, detail="Empty file or too large")
    dest = Path("uploads/events")
    dest.mkdir(parents=True, exist_ok=True)
    stored = f"{org.id}_{uuid.uuid4().hex}{allowed_mime[ctype]}"
    (dest / stored).write_bytes(blob)
    return {"success": True, "message": f"{kind} uploaded",
            "data": {"url": f"/uploads/events/{stored}", "kind": kind, "file_size": len(blob)}}


# ---------- organizer management (APPROVED only) ----------
def _own_event_or_403(event_id: int, org: OrganizerProfile, db: Session) -> Event:
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    if ev.organizer_id != org.id:
        raise HTTPException(status_code=403, detail="Not your event")
    return ev


def _parse_dt(value):
    if value is None or isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid datetime format (use ISO 8601)")


def _validate_event_payload(data: dict, db: Session, partial: bool = False):
    title = data.get("title")
    if not partial and not (title or "").strip():
        raise HTTPException(status_code=400, detail="Title is required")
    if "category_id" in data and data["category_id"] is not None:
        if not db.query(EventCategory).filter(EventCategory.id == data["category_id"]).first():
            raise HTTPException(status_code=400, detail="Invalid category_id")
    start, end = _parse_dt(data.get("start_date")), _parse_dt(data.get("end_date"))
    if not partial and start is None:
        raise HTTPException(status_code=400, detail="start_date is required")
    if start and end and end <= start:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")
    if data.get("max_capacity") is not None and int(data["max_capacity"]) < 1:
        raise HTTPException(status_code=400, detail="max_capacity must be >= 1")
    if data.get("price_min") is not None and float(data["price_min"]) < 0:
        raise HTTPException(status_code=400, detail="price_min cannot be negative")
    cover = data.get("cover_image_url")
    if cover:
        if not isinstance(cover, str) or len(cover) > 500 or not (
                cover.startswith(("http://", "https://", "/uploads/"))):
            raise HTTPException(status_code=400, detail="cover_image_url must be an http(s) URL or uploaded file path")
    video = data.get("video_url")
    if video:
        if not isinstance(video, str) or len(video) > 500 or not (
                video.startswith(("http://", "https://", "/uploads/"))):
            raise HTTPException(status_code=400, detail="video_url must be an http(s) URL or uploaded file path")
    types = data.get("ticket_types")
    if types is not None:
        if not isinstance(types, list) or not types or len(types) > 10:
            raise HTTPException(status_code=400, detail="ticket_types must be 1–10 entries")
        seen = set()
        for t in types:
            name = (t.get("name") or "").strip() if isinstance(t, dict) else ""
            if not name or name.lower() in seen:
                raise HTTPException(status_code=400, detail="Each ticket type needs a unique name")
            seen.add(name.lower())
            try:
                price, cap = float(t.get("price", 0)), int(t.get("capacity", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Bad price/capacity for '{name}'")
            if price < 0 or cap < 1:
                raise HTTPException(status_code=400, detail=f"Bad price/capacity for '{name}'")


@api_router.post("/events", tags=["Events"])
def create_event(event_data: dict, org: OrganizerProfile = Depends(require_organizer_profile), db: Session = Depends(get_db)):
    """Any organizer (even UNDER_REVIEW) may save drafts. Publishing needs approval."""
    _validate_event_payload(event_data, db)
    title = event_data["title"].strip()
    event = Event(
        organizer_id=org.id,
        category_id=event_data.get("category_id"),
        title=title,
        slug=title.lower().replace(" ", "-") + "-" + uuid.uuid4().hex[:8],
        short_description=event_data.get("short_description"),
        full_description=event_data.get("full_description"),
        venue=event_data.get("venue"),
        address=event_data.get("address"),
        city=event_data.get("city"),
        start_date=_parse_dt(event_data.get("start_date")),
        end_date=_parse_dt(event_data.get("end_date")),
        max_capacity=int(event_data.get("max_capacity", 100)),
        status="DRAFT",
        is_featured=False,
        price_min=float(event_data.get("price_min", 0.0)),
        cover_image_url=event_data.get("cover_image_url"),
        video_url=event_data.get("video_url"),
    )
    db.add(event)
    db.flush()
    custom = event_data.get("ticket_types") or []
    if custom:
        for t in custom:
            db.add(TicketType(
                event_id=event.id, name=t["name"].strip(),
                description=t.get("description"),
                price=float(t.get("price", 0)), currency="NPR",
                capacity=int(t.get("capacity")), status="ACTIVE",
            ))
    else:
        # Default ticket type so detail pages always have something bookable.
        db.add(TicketType(
            event_id=event.id, name="General",
            price=event.price_min, currency="NPR",
            capacity=event.max_capacity, status="ACTIVE",
        ))
    db.commit()
    db.refresh(event)
    return {"success": True, "message": "Event created as draft", "data": serialize_event(event, db)}


@api_router.put("/events/{event_id}", tags=["Events"])
def update_event(event_id: int, event_data: dict, org: OrganizerProfile = Depends(require_organizer_profile), db: Session = Depends(get_db)):
    ev = _own_event_or_403(event_id, org, db)
    if str(getattr(ev.status, "value", ev.status)) == "CANCELLED":
        raise HTTPException(status_code=400, detail="Cancelled events cannot be edited")
    _validate_event_payload(event_data, db, partial=True)
    for field in ["title", "category_id", "short_description", "full_description", "venue",
                  "address", "city", "max_capacity", "price_min", "cover_image_url", "video_url"]:
        if field in event_data and event_data[field] is not None:
            setattr(ev, field, event_data[field])
    for field in ["start_date", "end_date"]:
        if field in event_data and event_data[field] is not None:
            setattr(ev, field, _parse_dt(event_data[field]))
    db.commit()
    db.refresh(ev)
    return {"success": True, "message": "Event updated", "data": serialize_event(ev, db, include_ticket_types=True)}


@api_router.patch("/events/{event_id}/publish", tags=["Events"])
def publish_event(event_id: int, org: OrganizerProfile = Depends(require_approved_organizer), db: Session = Depends(get_db)):
    ev = _own_event_or_403(event_id, org, db)
    status = str(getattr(ev.status, "value", ev.status))
    if status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Cancelled events cannot be published")
    if compute_lifecycle(ev.start_date, ev.end_date) == "ENDED":
        raise HTTPException(status_code=400, detail="Ended events cannot be published")
    ev.status = "PUBLISHED"
    db.commit()
    return {"success": True, "message": "Event published", "data": serialize_event(ev, db)}


@api_router.patch("/events/{event_id}/cancel", tags=["Events"])
def cancel_event(event_id: int, org: OrganizerProfile = Depends(require_organizer_profile), db: Session = Depends(get_db)):
    ev = _own_event_or_403(event_id, org, db)
    ev.status = "CANCELLED"
    # Close ticket sales; existing CONFIRMED registrations stay for refund handling (Phase 5/7).
    db.query(TicketType).filter(TicketType.event_id == ev.id).update({"status": "INACTIVE"})
    db.commit()
    return {"success": True, "message": "Event cancelled. New purchases blocked; existing tickets preserved.", "data": serialize_event(ev, db)}


@api_router.delete("/events/{event_id}", tags=["Events"])
def delete_event(event_id: int, org: OrganizerProfile = Depends(require_organizer_profile), db: Session = Depends(get_db)):
    """Soft-delete = cancel. Records are never hard-deleted (history + ledger)."""
    ev = _own_event_or_403(event_id, org, db)
    ev.status = "CANCELLED"
    db.query(TicketType).filter(TicketType.event_id == ev.id).update({"status": "INACTIVE"})
    db.commit()
    return {"success": True, "message": "Event cancelled (records preserved)"}


# ---------- organizer views (history keeps ended/cancelled) ----------
@api_router.get("/organizer/events", tags=["Organizer"])
def organizer_events(
    lifecycle: Optional[str] = None,
    user: UserModel = Depends(require_auth),
    db: Session = Depends(get_db),
):
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        return {"success": True, "items": [], "message": "No organizer profile"}
    events = db.query(Event).filter(Event.organizer_id == org.id).order_by(Event.start_date.desc()).all()
    items = [serialize_event(ev, db) for ev in events]
    if lifecycle:
        items = [i for i in items if i["lifecycle"] == lifecycle.upper()]
    return {"success": True, "items": items, "message": "Events retrieved"}


@api_router.get("/organizer/registrations", tags=["Organizer"])
def organizer_registrations(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        return {"success": True, "items": []}
    regs = db.query(Registration).join(Event).filter(Event.organizer_id == org.id).all()
    result = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        tt = db.query(TicketType).filter(TicketType.id == r.ticket_type_id).first()
        u = db.query(UserModel).filter(UserModel.id == r.user_id).first()
        result.append({
            "id": r.id, "event_title": ev.title if ev else "-",
            "user_name": u.username if u else "-",
            "ticket_type_name": tt.name if tt else "-",
            "registration_date": r.registration_date,
            "status": str(getattr(r.status, "value", r.status)),
        })
    return {"success": True, "items": result, "message": "Registrations retrieved"}


@api_router.get("/organizer/stats", tags=["Dashboard"])
def organizer_stats(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer profile not found")
    return {"success": True, "data": get_dashboard_stats_organizer(org.id, db)}


# ---------- user history (lifecycle-aware, tickets stay accessible) ----------
@api_router.get("/user/upcoming", tags=["User"])
def user_upcoming(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    regs = db.query(Registration).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    result = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        if ev and compute_lifecycle(ev.start_date, ev.end_date) == "UPCOMING":
            result.append(serialize_event(ev, db))
    return {"success": True, "items": result}


@api_router.get("/user/past", tags=["User"])
def user_past(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    regs = db.query(Registration).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    result = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        if ev and compute_lifecycle(ev.start_date, ev.end_date) == "ENDED":
            result.append(serialize_event(ev, db))
    return {"success": True, "items": result}


@api_router.get("/user/stats", tags=["Dashboard"])
def user_stats(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    total = db.query(func.count(Registration.id)).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").scalar() or 0
    regs = db.query(Registration).filter(
        Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    upcoming = sum(
        1 for r in regs
        if (ev := db.query(Event).filter(Event.id == r.event_id).first())
        and compute_lifecycle(ev.start_date, ev.end_date) == "UPCOMING"
    )
    fav_count = db.query(func.count(Favorite.id)).filter(Favorite.user_id == user.id).scalar() or 0
    return {"success": True, "data": {"total_registrations": total, "upcoming": upcoming, "saved": fav_count}}


# ---------- favorites (fixed auth, same behavior) ----------
@api_router.post("/favorites", tags=["Favorites"])
def add_favorite(data: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    event_id = data.get("event_id")
    if not event_id:
        raise HTTPException(status_code=400, detail="event_id required")
    try:
        db.add(Favorite(user_id=user.id, event_id=event_id))
        db.commit()
        return {"success": True, "message": "Event saved"}
    except Exception:
        db.rollback()
        return {"success": True, "message": "Already saved"}


@api_router.delete("/favorites/{event_id}", tags=["Favorites"])
def remove_favorite(event_id: int, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.event_id == event_id).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"success": True, "message": "Event removed from saved"}


@api_router.get("/user/saved", tags=["Favorites"])
def get_saved(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    favs = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    ids = [f.event_id for f in favs]
    if not ids:
        return {"success": True, "items": []}
    return {"success": True, "items": [serialize_event(ev, db) for ev in db.query(Event).filter(Event.id.in_(ids)).all()],
            "message": "Saved events retrieved"}


# ---------- registrations (compat path used by EventDetailPage; canonical: /registrations) ----------
@api_router.post("/registrations", tags=["Registrations"])
def create_registration(data: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    from app.services.booking import BookingError, create_booking

    try:
        out = create_booking(db, user, data.get("event_id"), data.get("ticket_type_id"))
    except BookingError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    reg = out["registration"]
    if out["payment_required"]:
        return {"success": True, "message": "Order created. Complete payment to get your ticket.",
                "data": {"registration_id": reg.id, "payment_required": True, "amount": out["amount"]}}
    t = out["ticket"]
    return {"success": True, "message": "Registration successful",
            "data": {"registration_id": reg.id, "ticket_id": t.id,
                     "ticket_code": t.ticket_code, "qr_token": t.qr_token,
                     "qr_code_url": t.qr_code_url, "payment_required": False}}


@api_router.post("/checkins/verify", tags=["Check-in"])
def verify_checkin(data: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    """Compat path (CheckInPage v1). Ownership derived from the ticket's event."""
    from app.models.organizer import OrganizerProfile
    from app.models.ticket import Registration as RegModel
    from app.models.ticket import Ticket as TicketModel

    token = (data.get("qr_token") or "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="QR token required")
    ticket = db.query(TicketModel).filter(TicketModel.qr_token == token).first()
    if not ticket:
        ticket = db.query(TicketModel).filter(TicketModel.ticket_code == token).first()
    if not ticket:
        raise HTTPException(status_code=400, detail={"valid": False, "error": "INVALID_TICKET",
                                                     "message": "This ticket could not be verified."})
    reg = db.query(RegModel).filter(RegModel.id == ticket.registration_id).first()
    ev = db.query(Event).filter(Event.id == reg.event_id).first() if reg else None
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org or not ev or ev.organizer_id != org.id:
        raise HTTPException(status_code=403, detail={"valid": False, "error": "WRONG_EVENT",
                                                     "message": "You are not the organizer of this event."})
    if str(getattr(reg.status, "value", reg.status)) != "CONFIRMED" or \
       str(getattr(reg.payment_status, "value", reg.payment_status)) != "PAID":
        raise HTTPException(status_code=400, detail={"valid": False, "error": "NOT_PAID",
                                                     "message": "Ticket is not paid/confirmed."})
    tstatus = str(getattr(ticket.status, "value", ticket.status))
    if tstatus == "USED":
        raise HTTPException(status_code=400, detail={"valid": False, "error": "ALREADY_USED",
                                                     "message": "TICKET ALREADY USED"})
    if tstatus != "VALID":
        raise HTTPException(status_code=400, detail={"valid": False, "error": "INVALID_TICKET",
                                                     "message": "Ticket cannot be used."})
    result = check_in_ticket(ticket.qr_token, user.id, db)
    if result["valid"]:
        attendee = db.query(UserModel).filter(UserModel.id == reg.user_id).first()
        return {"success": True, "message": "ATTENDANCE CONFIRMED",
                "data": {**result["ticket"], "attendee": attendee.username if attendee else "-",
                         "event": ev.title, "valid": True}}
    raise HTTPException(status_code=400, detail={"valid": False, "error": result["error"], "message": result["message"]})


# ---------- admin (canonical home: admin_router; kept here only as redirect-safe stubs) ----------
# NOTE: /admin/stats and /admin/events live in admin_router (registered after
# this router would shadow them, so they are intentionally NOT defined here).
