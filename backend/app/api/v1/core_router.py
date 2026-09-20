"""EventFlow - Comprehensive API Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User as UserModel
from app.models.event import Event, EventCategory
from app.models.ticket import Registration, TicketType, Ticket, TicketScan
from app.models.other import EventReview, Favorite, Notification, OrganizerProfile, AuditLog, Report
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, generate_qr_token
from app.core.config import settings
from app.schemas import ResponseModel, PaginationParams, PaginationResult
from sqlalchemy import func, desc, and_
import qrcode
import io
import os
import sys
import uuid
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter()


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


def get_current_active_user(token: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user or not user.is_active:
        return None
    return user


# Health
@api_router.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "service": "EventFlow API"}


# Root
@api_router.get("/", tags=["Root"])
def root():
    return ResponseModel(success=True, message="EventFlow API v1", data={"version": "1.0.0"})
