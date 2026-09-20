from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.event import Event
from app.models.event_category import EventCategory
from app.models.ticket import TicketType
from app.models.other import EventReview, Favorite, Notification, OrganizerProfile
from app.schemas import CategoryCreate, CategoryResponse, ReviewCreate
from app.core.security import verify_token
from app.core.config import settings
from sqlalchemy import func
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/categories", tags=["Categories"])


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not token:
        return None
    payload = verify_token(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


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
