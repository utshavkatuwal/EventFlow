"""Organizers admin API — Phase 2 (verification statuses, documents, approve/reject)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.organizer import OrganizerProfile
from app.models.other import AuditLog
from app.models.user import User as UserModel
from app.models.verification import OrganizerApplication, OrganizerDocument, VerificationStatus

api_router = APIRouter(prefix="/organizers", tags=["Organizers"])


def _serialize(org: OrganizerProfile, db: Session) -> dict:
    user = db.query(UserModel).filter(UserModel.id == org.user_id).first()
    app = (
        db.query(OrganizerApplication)
        .filter(OrganizerApplication.user_id == org.user_id)
        .first()
    )
    docs = (
        db.query(OrganizerDocument)
        .filter(OrganizerDocument.user_id == org.user_id)
        .all()
    )
    return {
        "id": org.id,
        "user_id": org.user_id,
        "organization_name": org.organization_name,
        "description": org.description,
        "email": user.email if user else None,
        "phone": user.phone if user else org.phone,
        "city": org.city,
        "is_verified": bool(getattr(org, "is_verified", False)),
        "verification_status": getattr(org, "verification_status", "UNDER_REVIEW"),
        "rejection_reason": getattr(org, "rejection_reason", None),
        "submitted_at": app.submitted_at if app else org.created_at,
        "application_id": app.id if app else None,
        "documents": [
            {"id": d.id, "filename": d.filename, "mime_type": d.mime_type, "file_size": d.file_size}
            for d in docs
        ],
        "created_at": org.created_at,
    }


@api_router.get("/", response_model=dict)
def list_organizers(
    status: str | None = None,
    admin: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(OrganizerProfile).order_by(OrganizerProfile.created_at.desc())
    if status:
        q = q.filter(OrganizerProfile.verification_status == status.upper())
    orgs = q.all()
    return {"success": True, "items": [_serialize(o, db) for o in orgs], "message": "Organizers retrieved"}


@api_router.patch("/{org_id}/verify", response_model=dict)
def verify_organizer(org_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    """Legacy approve path (kept for compat) — prefers organizer-applications review."""
    org = db.query(OrganizerProfile).filter(OrganizerProfile.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")

    org.verification_status = "APPROVED"
    org.is_verified = True
    org.rejection_reason = None
    app = (
        db.query(OrganizerApplication)
        .filter(OrganizerApplication.user_id == org.user_id)
        .first()
    )
    if app:
        app.verification_status = VerificationStatus.APPROVED
        app.rejection_reason = None
    db.add(
        AuditLog(admin_user_id=admin.id, action="VERIFY_ORGANIZER", entity_type="organizer", entity_id=org_id, details={"verified": True})
    )
    db.commit()

    return {"success": True, "message": "Organizer verified"}


@api_router.patch("/{org_id}/reject", response_model=dict)
def reject_organizer(
    org_id: int, payload: dict, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)
):
    reason = (payload.get("rejection_reason") or "").strip()
    if not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    org = db.query(OrganizerProfile).filter(OrganizerProfile.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    org.verification_status = "REJECTED"
    org.is_verified = False
    org.rejection_reason = reason
    app = (
        db.query(OrganizerApplication)
        .filter(OrganizerApplication.user_id == org.user_id)
        .first()
    )
    if app:
        app.verification_status = VerificationStatus.REJECTED
        app.rejection_reason = reason
    db.add(
        AuditLog(admin_user_id=admin.id, action="REJECT_ORGANIZER", entity_type="organizer", entity_id=org_id, details={"reason": reason})
    )
    db.commit()
    return {"success": True, "message": "Organizer rejected"}
