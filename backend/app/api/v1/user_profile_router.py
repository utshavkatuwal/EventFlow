"""Self profile — Phase 9 (central auth). Serves GET|PATCH /users/me."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_roles, require_auth
from app.database import get_db
from app.models.organizer import OrganizerProfile
from app.models.user import User as UserModel

api_router = APIRouter(prefix="/users/me", tags=["User"])


def _serialize(user: UserModel, db: Session) -> dict:
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "account_type": getattr(user, "account_type", "USER") or "USER",
        "roles": get_user_roles(db, user.id),
        "role": "organizer" if org else "user",
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@api_router.get("", response_model=dict)
def get_me(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    return {"success": True, "data": _serialize(user, db), "message": "User info retrieved"}


@api_router.patch("", response_model=dict)
def update_me(payload: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    for field in ["first_name", "last_name", "phone", "avatar_url"]:
        if field in payload:
            setattr(user, field, payload[field])
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Profile updated", "data": _serialize(user, db)}
