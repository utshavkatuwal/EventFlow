from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User as UserModel
from app.models.organizer import OrganizerProfile
from app.core.security import get_current_active_user

api_router = APIRouter(prefix="/users/me", tags=["User"])


@api_router.get("", response_model=dict)
def get_me(user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)):
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


@api_router.patch("", response_model=dict)
def update_me(user_data: dict, user: UserModel = Depends(get_current_active_user), db: Session = Depends(get_db)):
    for field in ["first_name", "last_name", "phone", "avatar_url"]:
        if field in user_data:
            setattr(user, field, user_data[field])
    
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Profile updated", "data": {"id": user.id}}