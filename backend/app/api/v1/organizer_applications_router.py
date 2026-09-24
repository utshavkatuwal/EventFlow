"""Organizer verification: application, documents, admin approve/reject (Phase 1)."""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, require_auth
from app.core.config import settings
from app.database import get_db
from app.models.organizer import OrganizerProfile
from app.models.other import AuditLog
from app.models.user import User as UserModel
from app.models.verification import (
    OrganizerApplication,
    OrganizerDocument,
    VerificationStatus,
)

api_router = APIRouter(prefix="/organizer-applications", tags=["OrganizerVerification"])

ALLOWED_MIME = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_BYTES = 10 * 1024 * 1024


class ApplyIn(BaseModel):
    organization_name: str
    description: str | None = None
    verification_info: str | None = None


class ReviewIn(BaseModel):
    action: str  # APPROVE | REJECT
    rejection_reason: str | None = None


def _app_to_dict(app: OrganizerApplication, db: Session) -> dict:
    user = db.query(UserModel).filter(UserModel.id == app.user_id).first()
    docs = (
        db.query(OrganizerDocument)
        .filter(OrganizerDocument.application_id == app.id)
        .all()
    )
    return {
        "id": app.id,
        "user_id": app.user_id,
        "organizer_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
        "email": user.email if user else None,
        "phone": user.phone if user else None,
        "organization_name": app.organization_name,
        "description": app.description,
        "verification_info": app.verification_info,
        "verification_status": app.verification_status,
        "rejection_reason": app.rejection_reason,
        "submitted_at": app.submitted_at,
        "reviewed_at": app.reviewed_at,
        "documents": [
            {"id": d.id, "filename": d.filename, "mime_type": d.mime_type, "file_size": d.file_size}
            for d in docs
        ],
    }


@api_router.post("", response_model=dict)
def apply_or_resubmit(
    payload: ApplyIn, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)
):
    app = db.query(OrganizerApplication).filter(OrganizerApplication.user_id == user.id).first()
    if app and app.verification_status == VerificationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Application already approved")
    if not app:
        app = OrganizerApplication(user_id=user.id, organization_name=payload.organization_name)
        db.add(app)
    app.organization_name = payload.organization_name.strip()
    app.description = payload.description
    app.verification_info = payload.verification_info
    app.verification_status = VerificationStatus.UNDER_REVIEW
    app.rejection_reason = None
    app.submitted_at = datetime.utcnow()
    # mirror onto profile (dashboard banner reads this)
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        org = OrganizerProfile(user_id=user.id, organization_name=payload.organization_name.strip())
        db.add(org)
    org.organization_name = payload.organization_name.strip()
    org.description = payload.description
    org.verification_info = payload.verification_info
    org.verification_status = "UNDER_REVIEW"
    org.rejection_reason = None
    org.is_verified = False
    if getattr(user, "account_type", "USER") == "USER":
        user.account_type = "ORGANIZER"
    # ensure organizer role
    from app.models.user import Role, UserRole

    role = db.query(Role).filter(Role.name == "organizer").first()
    if role and not db.query(UserRole).filter(
        UserRole.user_id == user.id, UserRole.role_id == role.id
    ).first():
        db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    db.refresh(app)
    return {
        "success": True,
        "message": "Your organizer account is currently under review.",
        "data": _app_to_dict(app, db),
    }


@api_router.get("/me", response_model=dict)
def my_application(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    app = db.query(OrganizerApplication).filter(OrganizerApplication.user_id == user.id).first()
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not app and not org:
        raise HTTPException(status_code=404, detail="No organizer application found")
    status_value = (
        app.verification_status if app else getattr(org, "verification_status", "UNDER_REVIEW")
    )
    return {
        "success": True,
        "data": _app_to_dict(app, db)
        if app
        else {
            "verification_status": status_value,
            "organization_name": org.organization_name,
            "rejection_reason": getattr(org, "rejection_reason", None),
        },
    }


@api_router.post("/me/documents", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    user: UserModel = Depends(require_auth),
    db: Session = Depends(get_db),
):
    ctype = (file.content_type or "").lower()
    if ctype not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Only PDF, JPG, PNG, WEBP allowed")
    blob = await file.read()
    if len(blob) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    if len(blob) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    # extension allowlist (blocks executables)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".pdf", ".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail="File type not allowed")
    # app must exist (create draft shell if first upload before form)
    app = db.query(OrganizerApplication).filter(OrganizerApplication.user_id == user.id).first()
    if not app:
        raise HTTPException(status_code=400, detail="Submit the application form first")
    if app.verification_status == VerificationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Application already approved")
    dest_dir = Path(settings.VERIFICATION_DOC_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)
    stored = f"{user.id}_{uuid.uuid4().hex}{ALLOWED_MIME[ctype]}"
    (dest_dir / stored).write_bytes(blob)
    doc = OrganizerDocument(
        user_id=user.id,
        application_id=app.id,
        filename=file.filename,
        stored_path=str(dest_dir / stored),
        mime_type=ctype,
        file_size=len(blob),
    )
    db.add(doc)
    # resubmission after rejection re-opens review
    if app.verification_status == VerificationStatus.REJECTED:
        app.verification_status = VerificationStatus.UNDER_REVIEW
        app.rejection_reason = None
        org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
        if org:
            org.verification_status = "UNDER_REVIEW"
            org.rejection_reason = None
            org.is_verified = False
    db.commit()
    return {"success": True, "message": "Document uploaded", "data": {"id": doc.id, "filename": doc.filename}}


# ---------- admin ----------
@api_router.get("", response_model=dict)
def list_applications(
    status: str | None = None,
    admin: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(OrganizerApplication).order_by(OrganizerApplication.submitted_at.desc())
    if status:
        q = q.filter(OrganizerApplication.verification_status == status.upper())
    return {"success": True, "data": [_app_to_dict(a, db) for a in q.all()]}


@api_router.get("/{app_id}/documents/{doc_id}", response_model=dict)
def download_document_meta(
    app_id: int, doc_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)
):
    """Admin metadata endpoint. Actual bytes served by /{app_id}/documents/{doc_id}/file."""
    doc = (
        db.query(OrganizerDocument)
        .filter(OrganizerDocument.id == doc_id, OrganizerDocument.application_id == app_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "data": {"filename": doc.filename, "mime_type": doc.mime_type, "file_size": doc.file_size}}


@api_router.get("/{app_id}/documents/{doc_id}/file")
def download_document_file(
    app_id: int, doc_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)
):
    from fastapi.responses import FileResponse

    doc = (
        db.query(OrganizerDocument)
        .filter(OrganizerDocument.id == doc_id, OrganizerDocument.application_id == app_id)
        .first()
    )
    if not doc or not os.path.exists(doc.stored_path):
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(doc.stored_path, media_type=doc.mime_type or "application/octet-stream", filename=doc.filename)


@api_router.post("/{app_id}/review", response_model=dict)
def review_application(
    app_id: int, payload: ReviewIn, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)
):
    app = db.query(OrganizerApplication).filter(OrganizerApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    action = payload.action.upper()
    if action not in {"APPROVE", "REJECT"}:
        raise HTTPException(status_code=400, detail="action must be APPROVE or REJECT")
    if action == "REJECT" and not (payload.rejection_reason or "").strip():
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == app.user_id).first()
    if action == "APPROVE":
        app.verification_status = VerificationStatus.APPROVED
        app.rejection_reason = None
        if org:
            org.verification_status = "APPROVED"
            org.is_verified = True
            org.rejection_reason = None
    else:
        app.verification_status = VerificationStatus.REJECTED
        app.rejection_reason = payload.rejection_reason.strip()
        if org:
            org.verification_status = "REJECTED"
            org.is_verified = False
            org.rejection_reason = payload.rejection_reason.strip()
    app.reviewed_at = datetime.utcnow()
    app.reviewed_by_admin_id = admin.id
    db.add(
        AuditLog(
            admin_user_id=admin.id,
            action=f"ORGANIZER_{action}",
            entity_type="organizer_application",
            entity_id=app.id,
            details={"status": app.verification_status, "reason": app.rejection_reason},
        )
    )
    db.commit()
    return {"success": True, "message": f"Application {action.lower()}d", "data": _app_to_dict(app, db)}
