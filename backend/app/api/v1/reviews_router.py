"""Reviews — Phase 9 (central auth; confirmed attendance required)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_auth
from app.database import get_db
from app.models.event import Event
from app.models.other import EventReview
from app.models.ticket import Registration as RegistrationModel
from app.models.user import User as UserModel
from app.schemas import ReviewCreate

api_router = APIRouter(prefix="/reviews", tags=["Reviews"])


def _serialize(r: EventReview) -> dict:
    return {"id": r.id, "event_id": r.event_id, "user_id": r.user_id,
            "registration_id": r.registration_id, "rating": r.rating, "comment": r.comment,
            "is_reported": r.is_reported, "is_approved": r.is_approved,
            "created_at": r.created_at, "updated_at": r.updated_at}


@api_router.post("/", response_model=dict)
def create_review(review: ReviewCreate, user: UserModel = Depends(require_auth),
                  db: Session = Depends(get_db)):
    if not db.query(Event).filter(Event.id == review.event_id).first():
        raise HTTPException(status_code=404, detail="Event not found")
    if not (1 <= (review.rating or 0) <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1–5")
    registration = db.query(RegistrationModel).filter(
        RegistrationModel.user_id == user.id,
        RegistrationModel.event_id == review.event_id,
        RegistrationModel.status == "CONFIRMED",
    ).first()
    if not registration:
        raise HTTPException(status_code=403, detail="Must have a confirmed registration to review")
    if db.query(EventReview).filter(EventReview.user_id == user.id,
                                    EventReview.event_id == review.event_id).first():
        raise HTTPException(status_code=400, detail="Already reviewed this event")
    db_review = EventReview(event_id=review.event_id, user_id=user.id,
                            registration_id=registration.id,
                            rating=review.rating, comment=review.comment)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return {"success": True, "message": "Review created", "data": {"id": db_review.id}}


@api_router.get("/me", response_model=dict)
def my_reviews(user: UserModel = Depends(require_auth), db: Session = Depends(get_db)):
    rows = db.query(EventReview).filter(EventReview.user_id == user.id).order_by(EventReview.created_at.desc()).all()
    return {"success": True, "items": [_serialize(r) for r in rows]}
