"""Authentication router — Phase 1 (USER / ORGANIZER / ADMIN, RBAC-ready)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import rate_limit, require_auth
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.database import ensure_phase1_schema, get_db
from app.models.organizer import OrganizerProfile
from app.models.user import Role, User as UserModel, UserRole
from app.models.verification import OrganizerApplication, VerificationStatus

ensure_phase1_schema()

api_router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------- schemas ----------
class UserRegisterIn(BaseModel):
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=6)
    confirm_password: str | None = None
    username: str | None = None


class OrganizerRegisterIn(BaseModel):
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=6)
    confirm_password: str | None = None
    organization_name: str = Field(min_length=2)
    description: str | None = None
    verification_info: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


# ---------- helpers ----------
def _split_name(full: str | None, first: str | None, last: str | None):
    if first or last:
        return (first or "").strip() or None, (last or "").strip() or None
    if not full:
        return None, None
    parts = full.strip().split()
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])


def _ensure_role(db: Session, user_id: int, role_name: str) -> None:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name, description=f"Auto-created {role_name}")
        db.add(role)
        db.flush()
    if not (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
        .first()
    ):
        db.add(UserRole(user_id=user_id, role_id=role.id))
        db.flush()


def _role_names(db: Session, user_id: int) -> list[str]:
    rows = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    ids = [r.role_id for r in rows]
    if not ids:
        return []
    return [r.name for r in db.query(Role).filter(Role.id.in_(ids)).all()]


def _public_user(db: Session, user: UserModel) -> dict:
    roles = _role_names(db, user.id)
    account_type = getattr(user, "account_type", "USER") or "USER"
    data = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "account_type": account_type,
        "roles": roles,
        "is_active": user.is_active,
    }
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if org:
        data["organizer"] = {
            "organization_name": org.organization_name,
            "verification_status": getattr(org, "verification_status", "UNDER_REVIEW"),
            "rejection_reason": getattr(org, "rejection_reason", None),
            "is_verified": bool(getattr(org, "is_verified", False)),
        }
    return data


# ---------- endpoints ----------
@api_router.post("/register", dependencies=[Depends(rate_limit(20, 60))])
def register_user(payload: UserRegisterIn, db: Session = Depends(get_db)):
    if payload.confirm_password and payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    email = str(payload.email).lower().strip()
    if db.query(UserModel).filter(UserModel.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    username = (payload.username or email.split("@")[0]).strip()
    base, suffix = username, 0
    while db.query(UserModel).filter(UserModel.username == username).first():
        suffix += 1
        username = f"{base}{suffix}"
    first, last = _split_name(payload.full_name, payload.first_name, payload.last_name)
    user = UserModel(
        email=email,
        username=username,
        password_hash=hash_password(payload.password),
        first_name=first,
        last_name=last,
        phone=payload.phone,
        account_type="USER",
        is_active=True,
    )
    db.add(user)
    db.flush()
    _ensure_role(db, user.id, "user")
    db.commit()
    db.refresh(user)
    access = create_access_token({"sub": str(user.id), "role": "user", "account_type": "USER"})
    refresh = create_refresh_token({"sub": str(user.id)})
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {"user": _public_user(db, user), "user_id": user.id, "access_token": access, "refresh_token": refresh},
    }


@api_router.post("/organizer/register", dependencies=[Depends(rate_limit(20, 60))])
def register_organizer(payload: OrganizerRegisterIn, db: Session = Depends(get_db)):
    if payload.confirm_password and payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    email = str(payload.email).lower().strip()
    if db.query(UserModel).filter(UserModel.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    username = email.split("@")[0]
    base, suffix = username, 0
    while db.query(UserModel).filter(UserModel.username == username).first():
        suffix += 1
        username = f"{base}{suffix}"
    first, last = _split_name(payload.full_name, payload.first_name, payload.last_name)
    user = UserModel(
        email=email,
        username=username,
        password_hash=hash_password(payload.password),
        first_name=first,
        last_name=last,
        phone=payload.phone,
        account_type="ORGANIZER",
        is_active=True,
    )
    db.add(user)
    db.flush()
    org = OrganizerProfile(
        user_id=user.id,
        organization_name=payload.organization_name.strip(),
        description=payload.description,
        phone=payload.phone,
        verification_status="UNDER_REVIEW",
        verification_info=payload.verification_info,
        is_verified=False,
    )
    db.add(org)
    db.flush()
    db.add(
        OrganizerApplication(
            user_id=user.id,
            organization_name=payload.organization_name.strip(),
            description=payload.description,
            verification_info=payload.verification_info,
            verification_status=VerificationStatus.UNDER_REVIEW,
        )
    )
    _ensure_role(db, user.id, "organizer")
    db.commit()
    db.refresh(user)
    access = create_access_token({"sub": str(user.id), "role": "organizer", "account_type": "ORGANIZER"})
    refresh = create_refresh_token({"sub": str(user.id)})
    return {
        "success": True,
        "message": "Organizer application submitted. Your organizer account is currently under review.",
        "data": {"user": _public_user(db, user), "access_token": access, "refresh_token": refresh},
    }


@api_router.post("/login", dependencies=[Depends(rate_limit(30, 60))])
def login(payload: LoginIn, db: Session = Depends(get_db)):
    email = str(payload.email).lower().strip()
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    roles = _role_names(db, user.id)
    primary = roles[0] if roles else str(getattr(user, "account_type", "USER") or "USER").lower()
    access = create_access_token(
        {"sub": str(user.id), "role": primary, "account_type": getattr(user, "account_type", "USER")}
    )
    refresh = create_refresh_token({"sub": str(user.id)})
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": _public_user(db, user),
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "Bearer",
        },
        # backward-compat top-level keys used by current frontend
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
    }


@api_router.post("/refresh")
def refresh(payload: RefreshIn, db: Session = Depends(get_db)):
    data = verify_token(payload.refresh_token, "refresh")
    if not data or not data.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(UserModel).filter(UserModel.id == int(data["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    roles = _role_names(db, user.id)
    primary = roles[0] if roles else str(getattr(user, "account_type", "USER") or "USER").lower()
    access = create_access_token(
        {"sub": str(user.id), "role": primary, "account_type": getattr(user, "account_type", "USER")}
    )
    return {"success": True, "data": {"access_token": access, "token_type": "Bearer"},
            "access_token": access, "token_type": "Bearer"}


@api_router.get("/me")
def me(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    return {"success": True, "data": _public_user(db, user)}
