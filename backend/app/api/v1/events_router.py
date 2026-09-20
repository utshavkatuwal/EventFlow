from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User as UserModel, UserRole
from app.models.event import Event, EventCategory, EventStatus
from app.models.ticket import Registration, Ticket, TicketType
from app.models.other import EventReview, Favorite, Notification, OrganizerProfile
from app.services.public_service import get_event_stats
from app.services.auth_service import register_user, check_in_ticket
from app.services.analytics_service import get_admin_stats, get_dashboard_stats_organizer
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.schemas import (
    UserCreate, UserLogin, TokenPair, UserResponse, UserUpdate,
    EventCreate, EventUpdate, EventResponse,
    CategoryResponse, CategoryCreate,
    RegistrationRequest, RegistrationResponse,
    TicketResponse, TicketTypeResponse,
    ReviewCreate, ReviewResponse,
    NotificationResponse,
    ResponseModel, PaginationParams, PaginationResult,
)
from sqlalchemy import func, and_, desc
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter()


def get_current_user(
    token: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if not token:
        return None
    payload = verify_token(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


def get_current_active_user(
    token: Optional[str] = None,
    db: Session = Depends(get_db),
):
    user = get_current_user(token, db)
    if not user or not user.is_active:
        return None
    return user


# Root
@api_router.get("/", tags=["Root"])
def root():
    return ResponseModel(success=True, message="EventFlow API v1")


# Health
@api_router.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# Categories
@api_router.get("/categories", tags=["Categories"], response_model=dict)
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(EventCategory).all()
    return {"success": True, "items": [
        {"id": c.id, "name": c.name, "slug": c.slug, "description": c.description, "icon": c.icon, "created_at": c.created_at}
        for c in cats
    ], "message": "Categories retrieved successfully"}


# Events (Public)
@api_router.get("/events", tags=["Events"])
def list_events(
    page: int = 1,
    per_page: int = 20,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "start_date",
    db: Session = Depends(get_db),
):
    query = db.query(Event).join(UserModel).outerjoin(EventCategory)
    
    if category_id:
        query = query.filter(Event.category_id == category_id)
    if status:
        query = query.filter(Event.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Event.title.ilike(search_term) |
            Event.short_description.ilike(search_term) |
            Event.venue.ilike(search_term) |
            Event.city.ilike(search_term)
        )
    
    query = query.filter(Event.status.in_(["APPROVED", "PUBLISHED"]))
    
    if sort == "start_date":
        query = query.order_by(Event.start_date.asc())
    elif sort == "newest":
        query = query.order_by(Event.created_at.desc())
    elif sort == "popular":
        query = query.order_by(desc(func.count(Registration.id)))
    
    total = query.count()
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    
    organizer_profiles = db.query(OrganizerProfile).all()
    org_map = {op.user_id: op.organization_name for op in organizer_profiles}
    
    result_items = []
    for ev in items:
        organizer = db.query(OrganizerProfile).filter(OrganizerProfile.id == ev.organizer_id).first()
        category = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
        reg_count = db.query(func.count(Registration.id)).filter(Registration.event_id == ev.id, Registration.status == "CONFIRMED").scalar() or 0
        result_items.append({
            "id": ev.id,
            "organizer_id": ev.organizer_id,
            "category_id": ev.category_id,
            "title": ev.title,
            "slug": ev.slug,
            "short_description": ev.short_description,
            "cover_image_url": ev.cover_image_url,
            "venue": ev.venue,
            "address": ev.address,
            "city": ev.city,
            "country": ev.country,
            "start_date": ev.start_date,
            "end_date": ev.end_date,
            "max_capacity": ev.max_capacity,
            "status": ev.status,
            "is_featured": ev.is_featured,
            "price_min": ev.price_min,
            "organizer_name": organizer.organization_name if organizer else None,
            "category_name": category.name if category else None,
            "total_registrations": reg_count,
            "available_capacity": ev.max_capacity - reg_count,
            "created_at": ev.created_at,
            "updated_at": ev.updated_at,
        })
    
    return {
        "success": True,
        "items": result_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "message": "Events retrieved successfully"
    }


# Event Stats (for homepage)
@api_router.get("/events/stats", tags=["Events"])
def event_stats(db: Session = Depends(get_db)):
    stats = get_event_stats(db)
    return {"success": True, "data": stats, "message": "Stats retrieved"}


# Event Detail
@api_router.get("/events/{event_id}", tags=["Events"], response_model=dict)
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    
    organizer = db.query(OrganizerProfile).filter(OrganizerProfile.id == ev.organizer_id).first()
    category = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
    reg_count = db.query(func.count(Registration.id)).filter(Registration.event_id == ev.id, Registration.status == "CONFIRMED").scalar() or 0
    
    ticket_types = db.query(TicketType).filter(TicketType.event_id == event_id).all()
    
    return {
        "success": True,
        "data": {
            "id": ev.id,
            "organizer_id": ev.organizer_id,
            "category_id": ev.category_id,
            "title": ev.title,
            "slug": ev.slug,
            "short_description": ev.short_description,
            "full_description": ev.full_description,
            "cover_image_url": ev.cover_image_url,
            "venue": ev.venue,
            "address": ev.address,
            "city": ev.city,
            "country": ev.country,
            "start_date": ev.start_date,
            "end_date": ev.end_date,
            "max_capacity": ev.max_capacity,
            "status": ev.status,
            "is_featured": ev.is_featured,
            "price_min": ev.price_min,
            "organizer_name": organizer.organization_name if organizer else None,
            "category_name": category.name if category else None,
            "total_registrations": reg_count,
            "available_capacity": ev.max_capacity - reg_count,
            "ticket_types": [{"id": tt.id, "name": tt.name, "price": tt.price, "capacity": tt.capacity, "sold_count": tt.sold_count, "status": tt.status} for tt in ticket_types],
            "created_at": ev.created_at,
            "updated_at": ev.updated_at,
        },
        "message": "Event retrieved successfully"
    }


# Event Tickets
@api_router.get("/events/{event_id}/tickets", tags=["Events"])
def get_event_tickets(event_id: int, db: Session = Depends(get_db)):
    tickets = db.query(TicketType).filter(TicketType.event_id == event_id).all()
    return {"success": True, "items": [
        {"id": t.id, "event_id": t.event_id, "name": t.name, "description": t.description, "price": t.price, "currency": t.currency, "capacity": t.capacity, "sold_count": t.sold_count, "status": t.status, "created_at": t.created_at, "updated_at": t.updated_at}
        for t in tickets
    ], "message": "Tickets retrieved"}


# Auth: Register
@api_router.post("/auth/register", tags=["Auth"], response_model=dict)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = UserModel(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": True, "message": "User registered successfully", "data": {"user_id": new_user.id}}


# Auth: Login
@api_router.post("/auth/login", tags=["Auth"], response_model=TokenPair)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    role = "user"
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    if user_roles:
        role_obj = db.query(db.query(UserModel).join(UserRole).filter(UserRole.user_id == user.id).first())
    
    access_token = create_access_token({"sub": str(user.id), "role": role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


# Auth: Me
@api_router.get("/users/me", tags=["Users"])
def get_me(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "success": True,
        "data": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "role": "user",
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
        "message": "User info retrieved"
    }


# Registration
@api_router.post("/registrations", tags=["Registrations"], response_model=dict)
def create_registration(req: RegistrationRequest, token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        registration, ticket = register_user(req.event_id, user.id, req.ticket_type_id, db)
        return {
            "success": True,
            "message": "Registration successful",
            "data": {
                "registration_id": registration.id,
                "ticket_id": ticket.id,
                "ticket_code": ticket.ticket_code,
                "qr_token": ticket.qr_token,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Check-in
@api_router.post("/checkins/verify", tags=["Check-in"])
def verify_checkin(data: dict, db: Session = Depends(get_db)):
    qr_token = data.get("qr_token")
    scanned_by = data.get("scanned_by_user_id")
    if not qr_token:
        raise HTTPException(status_code=400, detail="QR token required")
    
    result = check_in_ticket(qr_token, scanned_by or 0, db)
    if result["valid"]:
        return {"success": True, "message": result["message"], "data": result["ticket"]}
    else:
        raise HTTPException(status_code=400, detail={"valid": False, "error": result["error"], "message": result["message"]})


# User Stats (Dashboard)
@api_router.get("/user/stats", tags=["Dashboard"])
def user_stats(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    total_reg = db.query(func.count(Registration.id)).filter(Registration.user_id == user.id, Registration.status == "CONFIRMED").scalar() or 0
    upcoming = db.query(func.count(Registration.id)).filter(
        Registration.user_id == user.id,
        Registration.status == "CONFIRMED",
        Event.start_date >= func.now()
    ).join(Event).scalar() or 0
    
    fav_count = db.query(func.count(Favorite.id)).filter(Favorite.user_id == user.id).scalar() or 0
    
    return {"success": True, "data": {"total_registrations": total_reg, "upcoming": upcoming, "saved": fav_count}}


# Organizer Stats
@api_router.get("/organizer/stats", tags=["Dashboard"])
def organizer_stats(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer profile not found")
    
    stats = get_dashboard_stats_organizer(org.id, db)
    return {"success": True, "data": stats}


# Admin Stats
@api_router.get("/admin/stats", tags=["Admin"])
def admin_stats(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    stats = get_admin_stats(db)
    return {"success": True, "data": stats}


# Simple event list for dashboards (mock with seeded data fallback)
@api_router.get("/organizer/events", tags=["Organizer"])
def organizer_events(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        return {"success": True, "items": [], "message": "No organizer profile"}
    events = db.query(Event).filter(Event.organizer_id == org.id).all()
    result = []
    for ev in events:
        cat = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
        result.append({
            "id": ev.id, "title": ev.title, "status": ev.status, "start_date": ev.start_date,
            "category_name": cat.name if cat else None, "organizer_name": org.organization_name,
        })
    return {"success": True, "items": result, "message": "Events retrieved"}


@api_router.get("/organizer/registrations", tags=["Organizer"])
def organizer_registrations(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
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
            "id": r.id, "event_title": ev.title if ev else "-", "user_name": u.username if u else "-",
            "ticket_type_name": tt.name if tt else "-", "registration_date": r.registration_date, "status": r.status,
        })
    return {"success": True, "items": result, "message": "Registrations retrieved"}


@api_router.get("/admin/events", tags=["Admin"])
def admin_events(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    events = db.query(Event).all()
    result = []
    for ev in events:
        org = db.query(OrganizerProfile).filter(OrganizerProfile.id == ev.organizer_id).first()
        cat = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
        result.append({
            "id": ev.id, "title": ev.title, "status": ev.status, "start_date": ev.start_date,
            "organizer_name": org.organization_name if org else None, "category_name": cat.name if cat else None,
        })
    return {"success": True, "items": result, "message": "Events retrieved"}


# Favorites
@api_router.post("/favorites", tags=["Favorites"], response_model=dict)
def add_favorite(data: dict, token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    event_id = data.get("event_id")
    if not event_id:
        raise HTTPException(status_code=400, detail="event_id required")
    existing = db.query(db.query(UserModel).join(Favorite).filter(Favorite.user_id == user.id, Favorite.event_id == event_id).first())
    try:
        from app.models.other import Favorite as FavoriteModel
        fav = FavoriteModel(user_id=user.id, event_id=event_id)
        db.add(fav)
        db.commit()
        return {"success": True, "message": "Event saved"}
    except Exception:
        db.rollback()
        return {"success": True, "message": "Already saved"}


@api_router.delete("/favorites/{event_id}", tags=["Favorites"], response_model=dict)
def remove_favorite(event_id: int, token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    from app.models.other import Favorite as FavoriteModel
    fav = db.query(FavoriteModel).filter(FavoriteModel.user_id == user.id, FavoriteModel.event_id == event_id).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"success": True, "message": "Event removed from saved"}


@api_router.get("/user/saved", tags=["Favorites"])
def get_saved(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    favs = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    event_ids = [f.event_id for f in favs]
    if not event_ids:
        return {"success": True, "items": []}
    from app.models.event import Event as EventModel
    from app.models.event_category import EventCategory
    events = db.query(EventModel).filter(EventModel.id.in_(event_ids)).all()
    result = []
    for ev in events:
        cat = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
        result.append({
            "id": ev.id, "title": ev.title, "category_name": cat.name if cat else None,
            "cover_image_url": ev.cover_image_url, "start_date": ev.start_date, "city": ev.city,
            "price_min": ev.price_min, "organizer_name": None,
        })
    return {"success": True, "items": result, "message": "Saved events retrieved"}


# User Upcoming/Past events
@api_router.get("/user/upcoming", tags=["User"])
def user_upcoming(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    from datetime import datetime
    regs = db.query(Registration).filter(Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    result = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        if ev and ev.start_date >= datetime.utcnow():
            cat = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
            result.append({
                "id": ev.id, "title": ev.title, "category_name": cat.name if cat else None,
                "cover_image_url": ev.cover_image_url, "start_date": ev.start_date, "city": ev.city,
                "price_min": ev.price_min, "organizer_name": None, "status": ev.status,
            })
    return {"success": True, "items": result}


@api_router.get("/user/past", tags=["User"])
def user_past(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    from datetime import datetime
    regs = db.query(Registration).filter(Registration.user_id == user.id, Registration.status == "CONFIRMED").all()
    result = []
    for r in regs:
        ev = db.query(Event).filter(Event.id == r.event_id).first()
        if ev and ev.start_date < datetime.utcnow():
            cat = db.query(EventCategory).filter(EventCategory.id == ev.category_id).first()
            result.append({
                "id": ev.id, "title": ev.title, "category_name": cat.name if cat else None,
                "cover_image_url": ev.cover_image_url, "start_date": ev.start_date, "city": ev.city,
                "price_min": ev.price_min, "organizer_name": None, "status": ev.status,
            })
    return {"success": True, "items": result}


# Event Creation (Organizer)
@api_router.post("/events", tags=["Events"])
def create_event(event_data: dict, token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_active_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Organizer profile required")
    
    event = Event(
        organizer_id=org.id,
        category_id=event_data.get("category_id"),
        title=event_data.get("title"),
        slug=event_data.get("title", "").lower().replace(" ", "-") + "-" + str(uuid.uuid4().hex[:8]),
        short_description=event_data.get("short_description"),
        full_description=event_data.get("full_description"),
        venue=event_data.get("venue"),
        address=event_data.get("address"),
        city=event_data.get("city"),
        start_date=event_data.get("start_date"),
        end_date=event_data.get("end_date"),
        max_capacity=event_data.get("max_capacity", 100),
        status=event_data.get("status", "DRAFT"),
        is_featured=event_data.get("is_featured", False),
        price_min=event_data.get("price_min", 0.0),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"success": True, "message": "Event created", "data": {"id": event.id}}
