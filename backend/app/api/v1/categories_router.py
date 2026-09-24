from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.user import User as UserModel
from app.models.event import Event, EventCategory
from app.models.ticket import TicketType
from app.models.other import EventReview, Favorite, Notification
from app.models.organizer import OrganizerProfile
from app.schemas import CategoryCreate, CategoryResponse, ReviewCreate
from app.core.security import verify_token
from app.core.config import settings
from app.models.other import AuditLog
from sqlalchemy import func
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/categories", tags=["Categories"])


@api_router.get("/", response_model=dict)
def list_categories(page: int = 1, per_page: int = 50, db: Session = Depends(get_db)):
    cats = db.query(EventCategory).offset((page-1)*per_page).limit(per_page).all()
    total = db.query(EventCategory).count()
    return {
        "success": True,
        "items": [
            {"id": c.id, "name": c.name, "slug": c.slug, "description": c.description, "icon": c.icon, "created_at": c.created_at}
            for c in cats
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "message": "Categories retrieved successfully"
    }


@api_router.get("/{category_id}", response_model=dict)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"success": True, "data": {"id": cat.id, "name": cat.name, "slug": cat.slug, "description": cat.description, "icon": cat.icon, "created_at": cat.created_at}, "message": "Category retrieved"}


@api_router.post("/", response_model=dict)
def create_category(payload: CategoryCreate, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    slug = (payload.name or "").strip().lower().replace(" ", "-")
    if db.query(EventCategory).filter((EventCategory.name == payload.name) | (EventCategory.slug == slug)).first():
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = EventCategory(name=payload.name.strip(), slug=slug, description=payload.description, icon=payload.icon)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    db.add(AuditLog(admin_user_id=admin.id, action="CREATE_CATEGORY", entity_type="category", entity_id=cat.id, details={"name": cat.name}))
    db.commit()
    return {"success": True, "message": "Category created", "data": {"id": cat.id, "name": cat.name, "slug": cat.slug}}


@api_router.patch("/{category_id}", response_model=dict)
def update_category(category_id: int, payload: dict, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    cat = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field in ("name", "description", "icon"):
        if field in payload and payload[field] is not None:
            setattr(cat, field, payload[field])
    db.commit()
    return {"success": True, "message": "Category updated"}


@api_router.delete("/{category_id}", response_model=dict)
def delete_category(category_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    cat = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if db.query(Event).filter(Event.category_id == category_id).count():
        raise HTTPException(status_code=400, detail="Category has events and cannot be deleted")
    db.delete(cat)
    db.commit()
    return {"success": True, "message": "Category deleted"}
