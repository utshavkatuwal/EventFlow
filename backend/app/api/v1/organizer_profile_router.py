"""Organizer Profile API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.organizer import OrganizerProfile
from app.core.security import verify_token

api_router = APIRouter(prefix="/organizer", tags=["Organizer"])


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


@api_router.get("/profile", response_model=dict)
def get_organizer_profile(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer profile not found")
    
    return {"success": True, "data": {
        "id": org.id,
        "user_id": org.user_id,
        "organization_name": org.organization_name,
        "description": org.description,
        "logo_url": org.logo_url,
        "website": org.website,
        "phone": org.phone,
        "address": org.address,
        "city": org.city,
        "country": org.country,
        "is_verified": org.is_verified,
        "created_at": org.created_at,
        "updated_at": org.updated_at,
    }}


@api_router.patch("/profile", response_model=dict)
def update_organizer_profile(profile_data: dict, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer profile not found")
    
    for field in ["organization_name", "description", "website", "phone", "address", "city", "country"]:
        if field in profile_data:
            setattr(org, field, profile_data[field])
    
    db.commit()
    db.refresh(org)
    
    return {"success": True, "message": "Profile updated", "data": {"id": org.id}}