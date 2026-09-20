import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.organizer import OrganizerProfile
from app.core.security import verify_token, hash_password
from app.schemas import UserUpdate
from datetime import datetime

api_router = APIRouter(prefix="/users", tags=["Users"])


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


def get_admin_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@api_router.get("/", response_model=dict)
def list_users(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    users = db.query(UserModel).all()
    return {
        "success": True,
        "items": [
            {"id": u.id, "email": u.email, "username": u.username, "first_name": u.first_name, "last_name": u.last_name, "role": "user", "is_active": u.is_active, "created_at": u.created_at}
            for u in users
        ],
        "message": "Users retrieved"
    }


@api_router.patch("/{user_id}/suspend", response_model=dict)
def suspend_user(user_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    from app.models.other import AuditLog
    audit = AuditLog(
        admin_user_id=admin.id,
        action="SUSPEND_USER",
        entity_type="user",
        entity_id=user_id,
        details={"suspended": not user.is_active},
    )
    db.add(audit)
    db.commit()
    
    return {"success": True, "message": f"User {'suspended' if not user.is_active else 'reactivated'}"}


@api_router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": {"id": user.id, "email": user.email, "username": user.username, "first_name": user.first_name, "last_name": user.last_name, "is_active": user.is_active, "role": "user"}}
