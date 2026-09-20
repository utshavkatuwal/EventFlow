import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.other import OrganizerProfile, AuditLog
from app.core.security import verify_token
from app.schemas import OrganizerCreate
from sqlalchemy import func
from datetime import datetime

api_router = APIRouter(prefix="/organizers", tags=["Organizers"])


def get_admin_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    from app.core.security import verify_token as vt
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


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
def list_organizers(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    orgs = db.query(OrganizerProfile).all()
    result = []
    for o in orgs:
        user = db.query(UserModel).filter(UserModel.id == o.user_id).first()
        result.append({
            "id": o.id,
            "user_id": o.user_id,
            "organization_name": o.organization_name,
            "description": o.description,
            "email": user.email if user else None,
            "username": user.username if user else None,
            "is_verified": o.is_verified,
            "created_at": o.created_at,
        })
    return {"success": True, "items": result, "message": "Organizers retrieved"}


@api_router.patch("/{org_id}/verify", response_model=dict)
def verify_organizer(org_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    org = db.query(OrganizerProfile).filter(OrganizerProfile.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    
    org.is_verified = True
    db.commit()
    
    audit = AuditLog(admin_user_id=admin.id, action="VERIFY_ORGANIZER", entity_type="organizer", entity_id=org_id, details={"verified": True})
    db.add(audit)
    db.commit()
    
    return {"success": True, "message": "Organizer verified"}
