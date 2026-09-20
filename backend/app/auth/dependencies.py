from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.core.security import verify_token
from app.core.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    token = None
    if credentials:
        token = credentials.credentials
    elif "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        return None

    payload = verify_token(token, "access")
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    return user


async def get_current_active_user(
    request: Request,
    db: Session = Depends(get_db),
):
    user = await get_current_user(request, db=db)
    if not user:
        return None
    if not user.is_active:
        return None
    return user


def require_role(*roles: str):
    async def role_checker(
        request: Request,
        db: Session = Depends(get_db),
    ):
        user = await get_current_user(request, db=db)
        if not user:
            return None
        # Check roles via user_roles table
        user_roles = db.query("UserRole").filter_by(user_id=user.id).all()
        user_role_names = []
        from app.models.user import UserRole as UserRoleModel
        role_ids = [ur.role_id for ur in user_roles] if user_roles else []
        if role_ids:
            roles_q = db.query(UserRoleModel).filter(UserRoleModel.id.in_(role_ids)).all()
            for r in roles_q:
                role_obj = db.query(Role).filter(Role.id == r.role_id).first()
                if role_obj:
                    user_role_names.append(role_obj.name)
        if not any(r in user_role_names for r in roles):
            return None
        return user
    return role_checker

from app.models.user import Role
