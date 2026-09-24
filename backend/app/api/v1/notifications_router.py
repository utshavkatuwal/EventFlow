"""Notifications — Phase 9 (central auth; sending is admin-only)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, require_auth
from app.database import get_db
from app.models.other import Notification
from app.models.user import User as UserModel

api_router = APIRouter(prefix="/notifications", tags=["Notifications"])


@api_router.get("/", response_model=dict)
def list_notifications(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()
    return {"success": True, "items": [
        {"id": n.id, "user_id": n.user_id, "title": n.title, "message": n.message, "type": n.type,
         "reference_type": n.reference_type, "reference_id": n.reference_id,
         "is_read": n.is_read, "created_at": n.created_at} for n in notifs],
        "message": "Notifications retrieved"}


@api_router.patch("/{notif_id}/read", response_model=dict)
def mark_read(notif_id: int, user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"success": True, "message": "Notification marked as read"}


@api_router.post("/send", response_model=dict)
def send_notification(data: dict, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    title = (data.get("title") or "").strip()
    message = (data.get("message") or "").strip()
    if not user_id or not title or not message:
        raise HTTPException(status_code=400, detail="user_id, title, and message required")
    if not db.query(UserModel).filter(UserModel.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    notif = Notification(user_id=user_id, title=title[:255], message=message,
                         type=str(data.get("type", "general"))[:50])
    db.add(notif)
    db.commit()
    return {"success": True, "message": "Notification sent", "data": {"id": notif.id}}
