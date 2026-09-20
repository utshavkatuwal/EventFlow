from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User as UserModel
from app.models.other import Favorite as FavoriteModel, OrganizerProfile, AuditLog
from app.core.security import verify_token, hash_password
from app.schemas import ResponseModel
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/auth", tags=["Auth"])


def get_current_user(token: Optional[str] = None, db: Session = Depends(get_db)):
    if not token:
        return None
    payload = verify_token(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


@api_router.post("/register", response_model=dict)
def register(user_data: dict, db: Session = Depends(get_db)):
    """Register a new user account"""
    from app.schemas import UserCreate
    try:
        data = UserCreate(**user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    existing = db.query(UserModel).filter(UserModel.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = UserModel(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": True, "message": "User registered successfully", "data": {"user_id": new_user.id}}


@api_router.post("/login")
def login(credentials: dict, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens"""
    from app.core.security import verify_password, create_access_token, create_refresh_token
    email = credentials.get("email")
    password = credentials.get("password")
    
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    access_token = create_access_token({"sub": str(user.id), "role": "user"})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}


@api_router.post("/refresh")
def refresh_token(token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    from app.core.security import verify_token, create_access_token
    payload = verify_token(token, "refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_access = create_access_token({"sub": payload.get("sub"), "role": payload.get("role", "user")})
    return {"access_token": new_access, "token_type": "Bearer"}
