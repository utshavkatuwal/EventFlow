from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.other import Favorite
from app.core.security import verify_token
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/user", tags=["User"])


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


@api_router.get("/stats", response_model=dict)
def user_stats(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.models.ticket import Registration as RegistrationModel, Ticket as TicketModel
    total_reg = db.query(RegistrationModel).filter(RegistrationModel.user_id == user.id, RegistrationModel.status == "CONFIRMED").count()
    
    from datetime import datetime
    upcoming = db.query(RegistrationModel).join(EventModel).filter(
        RegistrationModel.user_id == user.id,
        RegistrationModel.status == "CONFIRMED",
        EventModel.start_date >= datetime.utcnow(),
    ).count() if False else db.query(RegistrationModel).filter(
        RegistrationModel.user_id == user.id,
        RegistrationModel.status == "CONFIRMED",
    ).join(EventModel).filter(EventModel.start_date >= datetime.utcnow()).count()
    
    from app.models.other import Favorite as FavoriteModel
    saved = db.query(FavoriteModel).filter(FavoriteModel.user_id == user.id).count()
    
    return {"success": True, "data": {"total_registrations": total_reg, "upcoming": upcoming, "saved": saved}}


from app.models.event import Event as EventModel


@api_router.get("/upcoming", response_model=dict)
def user_upcoming(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from datetime import datetime
    from app.models.ticket import Registration as RegistrationModel
    regs = db.query(RegistrationModel).filter(RegistrationModel.user_id == user.id, RegistrationModel.status == "CONFIRMED").all()
    
    result = []
    for r in regs:
        ev = db.query(EventModel).filter(EventModel.id == r.event_id).first()
        if ev and ev.start_date >= datetime.utcnow():
            result.append({
                "id": ev.id, "title": ev.title, "category_id": ev.category_id,
                "cover_image_url": ev.cover_image_url, "start_date": ev.start_date,
                "city": ev.city, "price_min": ev.price_min, "status": ev.status,
                "organizer_name": None, "category_name": None,
            })
    
    return {"success": True, "items": result}


@api_router.get("/past", response_model=dict)
def user_past(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from datetime import datetime
    from app.models.ticket import Registration as RegistrationModel
    regs = db.query(RegistrationModel).filter(RegistrationModel.user_id == user.id, RegistrationModel.status == "CONFIRMED").all()
    
    result = []
    for r in regs:
        ev = db.query(EventModel).filter(EventModel.id == r.event_id).first()
        if ev and ev.start_date < datetime.utcnow():
            result.append({
                "id": ev.id, "title": ev.title, "category_id": ev.category_id,
                "cover_image_url": ev.cover_image_url, "start_date": ev.start_date,
                "city": ev.city, "price_min": ev.price_min, "status": ev.status,
                "organizer_name": None, "category_name": None,
            })
    
    return {"success": True, "items": result}


@api_router.get("/me", response_model=dict)
def get_me(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.models.other import OrganizerProfile
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    
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
            "role": "organizer" if org else "user",
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
        "message": "User info retrieved"
    }


@api_router.patch("/me", response_model=dict)
def update_me(user_data: dict, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    for field in ["first_name", "last_name", "phone", "avatar_url"]:
        if field in user_data:
            setattr(user, field, user_data[field])
    
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Profile updated", "data": {"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "phone": user.phone}}
