from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User as UserModel
from app.models.other import EventReview
from app.core.security import verify_token
from app.schemas import ReviewCreate
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

api_router = APIRouter(prefix="/reviews", tags=["Reviews"])


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


@api_router.post("/", response_model=dict)
def create_review(review: ReviewCreate, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user has a valid registration for this event
    reg = db.query(db.query(UserModel).join(EventReview).filter(EventReview.user_id == user.id, EventReview.event_id == review.event_id).first())
    from app.models.ticket import Registration as RegistrationModel
    registration = db.query(RegistrationModel).filter(
        RegistrationModel.user_id == user.id,
        RegistrationModel.event_id == review.event_id,
        RegistrationModel.status == "CONFIRMED",
    ).first()
    
    if not registration:
        raise HTTPException(status_code=403, detail="Must have a confirmed registration to review")
    
    # Check for duplicate review
    existing = db.query(EventReview).filter(
        EventReview.user_id == user.id,
        EventReview.event_id == review.event_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already reviewed this event")
    
    db_review = EventReview(
        event_id=review.event_id,
        user_id=user.id,
        registration_id=registration.id,
        rating=review.rating,
        comment=review.comment,
    )
    db.add(db_review)
    db.commit()
    return {"success": True, "message": "Review created", "data": {"id": db_review.id}}
