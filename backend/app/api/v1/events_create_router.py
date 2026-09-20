"""Event Creation API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.organizer import OrganizerProfile
from app.models.event import Event
from app.core.security import verify_token
import uuid

api_router = APIRouter(prefix="/events", tags=["Events"])


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    if not token:
        return None
    from app.core.security import verify_token as vt
    payload = vt(token, "access")
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(UserModel).filter(UserModel.id == int(user_id)).first()


@api_router.post("", response_model=dict)
def create_event(event_data: dict, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    org = db.query(OrganizerProfile).filter(OrganizerProfile.user_id == user.id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Organizer profile required")
    
    title = event_data.get("title", "")
    event = Event(
        organizer_id=org.id,
        category_id=event_data.get("category_id"),
        title=title,
        slug=title.lower().replace(" ", "-") + "-" + str(uuid.uuid4().hex[:8]),
        short_description=event_data.get("short_description"),
        full_description=event_data.get("full_description"),
        venue=event_data.get("venue"),
        address=event_data.get("address"),
        city=event_data.get("city"),
        start_date=event_data.get("start_date"),
        end_date=event_data.get("end_date"),
        max_capacity=event_data.get("max_capacity", 100),
        status=event_data.get("status", "DRAFT"),
        is_featured=event_data.get("is_featured", False),
        price_min=event_data.get("price_min", 0.0),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"success": True, "message": "Event created", "data": {"id": event.id}}