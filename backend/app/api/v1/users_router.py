"""Users admin API — Phase 2 (central auth, account types)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_roles, require_admin
from app.database import get_db
from app.models.other import AuditLog
from app.models.user import User as UserModel

api_router = APIRouter(prefix="/users", tags=["Users"])


def _serialize(u: UserModel, db: Session) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "phone": u.phone,
        "account_type": getattr(u, "account_type", "USER") or "USER",
        "roles": get_user_roles(db, u.id),
        "is_active": u.is_active,
        "created_at": u.created_at,
    }


@api_router.get("/", response_model=dict)
def list_users(admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(UserModel).order_by(UserModel.created_at.desc()).all()
    return {"success": True, "items": [_serialize(u, db) for u in users], "message": "Users retrieved"}


@api_router.patch("/{user_id}/suspend", response_model=dict)
def suspend_user(user_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot suspend your own admin account")

    user.is_active = not user.is_active
    db.commit()

    db.add(
        AuditLog(
            admin_user_id=admin.id,
            action="SUSPEND_USER",
            entity_type="user",
            entity_id=user_id,
            details={"suspended": not user.is_active},
        )
    )
    db.commit()

    return {"success": True, "message": f"User {'suspended' if not user.is_active else 'reactivated'}"}


@api_router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": _serialize(user, db)}
