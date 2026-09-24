"""Organizer Profile API — Phase 2 (central auth, verification status)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_roles, require_admin, require_auth
from app.database import get_db
from app.models.organizer import OrganizerProfile
from app.models.user import User as UserModel

api_router = APIRouter(prefix="/organizer", tags=["Organizer"])


def _serialize(org: OrganizerProfile) -> dict:
    return {
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
        "is_verified": bool(getattr(org, "is_verified", False)),
        "verification_status": getattr(org, "verification_status", "UNDER_REVIEW"),
        "verification_info": getattr(org, "verification_info", None),
        "rejection_reason": getattr(org, "rejection_reason", None),
        "created_at": org.created_at,
        "updated_at": org.updated_at,
    }


@api_router.get("/profile", response_model=dict)
def get_organizer_profile(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer profile not found")
    return {"success": True, "data": _serialize(org)}


@api_router.patch("/profile", response_model=dict)
def update_organizer_profile(
    profile_data: dict, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)
):
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer profile not found")

    for field in ["organization_name", "description", "website", "phone", "address", "city", "country"]:
        if field in profile_data and profile_data[field] is not None:
            setattr(org, field, profile_data[field])

    db.commit()
    db.refresh(org)
    return {"success": True, "message": "Profile updated", "data": _serialize(org)}


@api_router.get("/verification-status", response_model=dict)
def verification_status(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    """Lightweight status endpoint used by the dashboard banner (Phase 2)."""
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        return {"success": True, "data": {"is_organizer": False}}
    return {
        "success": True,
        "data": {
            "is_organizer": True,
            "verification_status": getattr(org, "verification_status", "UNDER_REVIEW"),
            "rejection_reason": getattr(org, "rejection_reason", None),
            "is_verified": bool(getattr(org, "is_verified", False)),
            "roles": get_user_roles(db, user.id),
        },
    }
