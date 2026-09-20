from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User as UserModel
from app.core.security import verify_token
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/users/me", tags=["User"])


def get_current_user(token: Optional[str] = None, db: Session = Depends(get_db)):
    if not token:
        return None
    payload = verify_token(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


@api_router.get("", response_model=dict)
def get_me(token: Optional[str] = None, db: Session = Depends(get_db)):
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


@api_router.patch("", response_model=dict)
def update_me(user_data: dict, token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    for field in ["first_name", "last_name", "phone", "avatar_url"]:
        if field in user_data:
            setattr(user, field, user_data[field])
    
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Profile updated", "data": {"id": user.id}}
