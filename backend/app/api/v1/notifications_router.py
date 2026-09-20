from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.other import Notification
from app.core.security import verify_token, create_access_token
from app.core.config import settings
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not token:
        return None
    payload = verify_token(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


@api_router.get("/", response_model=dict)
def list_notifications(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    notifs = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()
    return {
        "success": True,
        "items": [
            {"id": n.id, "user_id": n.user_id, "title": n.title, "message": n.message, "type": n.type, "reference_type": n.reference_type, "reference_id": n.reference_id, "is_read": n.is_read, "created_at": n.created_at}
            for n in notifs
        ],
        "message": "Notifications retrieved"
    }


@api_router.patch("/{notif_id}/read", response_model=dict)
def mark_read(notif_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notif.is_read = True
    db.commit()
    return {"success": True, "message": "Notification marked as read"}


@api_router.post("/send", response_model=dict)
def send_notification(data: dict, db: Session = Depends(get_db)):
    from app.models.user import User as UserModel
    user_id = data.get("user_id")
    title = data.get("title")
    message = data.get("message")
    ntype = data.get("type", "general")
    
    if not user_id or not title or not message:
        raise HTTPException(status_code=400, detail="user_id, title, and message required")
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notif = Notification(user_id=user_id, title=title, message=message, type=ntype)
    db.add(notif)
    db.commit()
    return {"success": True, "message": "Notification sent", "data": {"id": notif.id}}