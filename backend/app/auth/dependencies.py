"""Central authentication + RBAC dependencies (Phase 1).

All protected endpoints MUST use these helpers — never trust frontend-only guards.
Token is read from HTTPBearer first, then raw Authorization header as fallback.
"""
from __future__ import annotations

import os
import time
from collections import defaultdict
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.database import get_db

security = HTTPBearer(auto_error=False)

# --- simple in-memory rate limiter (auth / payment sensitive endpoints) ---
_rate_buckets: dict = defaultdict(list)


def rate_limit(times: int = 20, seconds: int = 60):
    """Dependency factory: max `times` requests per `seconds` per client IP."""

    async def checker(request: Request):
        if os.getenv("EVENTFLOW_TESTING"):
            return
        key = request.client.host if request.client else "unknown"
        now = time.time()
        window = _rate_buckets[key]
        # prune
        cutoff = now - seconds
        while window and window[0] < cutoff:
            window.pop(0)
        if len(window) >= times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )
        window.append(now)

    return checker


def _extract_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials],
) -> Optional[str]:
    if credentials and credentials.credentials:
        return credentials.credentials
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Return current User or None (no exception — for public routes)."""
    from app.models.user import User as UserModel

    token = _extract_token(request, credentials)
    if not token:
        return None
    payload = verify_token(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        return db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    except Exception:
        return None


async def require_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request, credentials, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return user


def get_user_roles(db: Session, user_id: int) -> List[str]:
    """Resolve role names via user_roles join. Tolerant of missing tables."""
    try:
        from app.models.user import Role, UserRole

        rows = db.query(UserRole).filter(UserRole.user_id == user_id).all()
        role_ids = [r.role_id for r in rows]
        if not role_ids:
            return []
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        return [r.name for r in roles]
    except Exception:
        return []


def require_roles(*roles: str):
    """Dependency: user must have at least one of `roles`. Raises 401/403."""

    async def checker(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db),
    ):
        user = await get_current_user(request, credentials, db)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if not getattr(user, "is_active", True):
            raise HTTPException(status_code=403, detail="Account is deactivated")
        names = get_user_roles(db, user.id)
        # Backward compat: legacy admins may lack a role row but have
        # account_type == ADMIN on the user model.
        account_type = getattr(user, "account_type", None)
        if account_type:
            names = list(set(names + [str(account_type).lower()]))
        wanted = {r.lower() for r in roles}
        if not (set(n.lower() for n in names) & wanted):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return checker


require_admin = require_roles("admin")


async def require_organizer_profile(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Any user with an organizer profile (regardless of verification)."""
    from app.models.organizer import OrganizerProfile

    user = await require_auth(request, credentials, db)
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Organizer profile required")
    return org


async def require_approved_organizer(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Only APPROVED organizers (UNDER_REVIEW / REJECTED get 403 with reason)."""
    from app.models.organizer import OrganizerProfile

    user = await require_auth(request, credentials, db)
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Organizer profile required")
    status_value = getattr(org, "verification_status", None)
    if status_value is None:
        # Legacy column: is_verified bool
        if not getattr(org, "is_verified", False):
            raise HTTPException(
                status_code=403,
                detail="Your organizer account is currently under review.",
            )
        return org
    if str(status_value).upper() != "APPROVED":
        reason = getattr(org, "rejection_reason", None)
        msg = "Your organizer account is currently under review."
        if str(status_value).upper() == "REJECTED" and reason:
            msg = f"Organizer application rejected: {reason}"
        raise HTTPException(status_code=403, detail=msg)
    return org


# Backwards-compatible alias (old name was require_role)
require_role = require_roles
