import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User as UserModel
from app.models.other import Report, AuditLog
from app.core.security import verify_token
from app.schemas import ResponseModel
from datetime import datetime

api_router = APIRouter(prefix="/admin", tags=["Admin"])


def get_admin_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    from app.core.security import verify_token as vt
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


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


@api_router.get("/stats", response_model=dict)
def admin_stats(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    
    total_users = db.query(UserModel).filter(UserModel.is_active == True).count()
    total_organizers = db.query(OrganizerProfile).count() if False else db.query(db.query(UserModel).join(OrganizerProfile).exists()).count()
    from app.models.other import OrganizerProfile
    total_organizers = db.query(OrganizerProfile).count()
    total_events = db.query(Event).count() if False else _count(db, Event)
    from app.models.event import Event
    published_events = db.query(Event).filter(Event.status.in_(["APPROVED", "PUBLISHED"])).count()
    pending_events = db.query(Event).filter(Event.status == "PENDING_REVIEW").count()
    
    from app.models.ticket import Registration as RegistrationModel
    total_registrations = db.query(RegistrationModel).filter(RegistrationModel.status == "CONFIRMED").count()
    
    from app.models.ticket import Ticket as TicketModel
    total_attendees = db.query(TicketModel).filter(TicketModel.status == "USED").count()
    
    from app.models.other import EventReview
    total_reviews = db.query(EventReview).count()
    open_reports = db.query(Report).filter(Report.status == "OPEN").count()
    
    return {
        "success": True,
        "data": {
            "total_users": total_users,
            "total_organizers": total_organizers,
            "total_events": total_events,
            "published_events": published_events,
            "pending_events": pending_events,
            "total_registrations": total_registrations,
            "total_attendees": total_attendees,
            "total_reviews": total_reviews,
            "open_reports": open_reports,
        }
    }


from app.models.event import Event


@api_router.patch("/events/{event_id}/approve", response_model=dict)
def approve_event(event_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = "APPROVED"
    db.commit()
    
    audit = AuditLog(admin_user_id=admin.id, action="APPROVE_EVENT", entity_type="event", entity_id=event_id, details={"status": "APPROVED"})
    db.add(audit)
    db.commit()
    
    return {"success": True, "message": "Event approved"}


@api_router.patch("/events/{event_id}/reject", response_model=dict)
def reject_event(event_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = "REJECTED"
    db.commit()
    
    audit = AuditLog(admin_user_id=admin.id, action="REJECT_EVENT", entity_type="event", entity_id=event_id, details={"status": "REJECTED"})
    db.add(audit)
    db.commit()
    
    return {"success": True, "message": "Event rejected"}


@api_router.get("/reports", response_model=dict)
def list_reports(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return {
        "success": True,
        "items": [
            {"id": r.id, "report_type": r.report_type, "reference_type": r.reference_type, "reference_id": r.reference_id, "reason": r.reason, "status": r.status, "created_at": r.created_at}
            for r in reports
        ]
    }


@api_router.patch("/reports/{report_id}/resolve", response_model=dict)
def resolve_report(report_id: int, token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.status = "RESOLVED"
    report.resolved_by_admin_id = admin.id
    db.commit()
    
    return {"success": True, "message": "Report resolved"}


@api_router.get("/audit-logs", response_model=dict)
def audit_logs(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    admin = get_admin_user(token, db)
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    from app.models.user import User as UserModel
    result = []
    for log in logs:
        admin_user = db.query(UserModel).filter(UserModel.id == log.admin_user_id).first()
        result.append({
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "admin_name": admin_user.username if admin_user else None,
            "created_at": log.created_at,
        })
    return {"success": True, "items": result}
