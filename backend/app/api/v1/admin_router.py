"""Admin control plane — Phase 8 (central auth, full statistics).

Canonical home for /admin/* (legacy duplicates in events_router were removed).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.event import Event
from app.models.finance import Payment, PaymentStatus, PlatformSetting, Wallet, WithdrawalRequest
from app.models.organizer import OrganizerProfile
from app.models.other import AuditLog, EventReview, Report
from app.models.ticket import Registration, Ticket
from app.models.user import User as UserModel
from app.models.verification import OrganizerApplication
from app.services.lifecycle import compute_lifecycle

api_router = APIRouter(prefix="/admin", tags=["Admin"])

EDITABLE_SETTINGS = {
    "withdrawal_service_fee": float,
    "platform_ticket_fee": float,
    "settlement_hold_days": int,
}


@api_router.get("/stats", response_model=dict)
def admin_stats(admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    now_active_statuses = ["APPROVED", "PUBLISHED"]
    events = db.query(Event).all()
    lifecycles = [compute_lifecycle(e.start_date, e.end_date) for e in events]
    active = sum(
        1 for e, lc in zip(events, lifecycles)
        if str(getattr(e.status, "value", e.status)) in now_active_statuses and lc != "ENDED"
    )
    volume = (
        db.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(Payment.status == PaymentStatus.COMPLETED)
        .scalar()
        or 0.0
    )
    wallets = db.query(Wallet).all()
    pending_wd = db.query(WithdrawalRequest).filter(WithdrawalRequest.status == "PENDING").all()
    paid_wd = (
        db.query(func.coalesce(func.sum(WithdrawalRequest.requested_amount), 0.0))
        .filter(WithdrawalRequest.status == "PAID")
        .scalar()
        or 0.0
    )
    return {
        "success": True,
        "data": {
            "total_users": db.query(UserModel).filter(UserModel.is_active == True).count(),  # noqa: E712
            "total_organizers": db.query(OrganizerProfile).count(),
            "pending_organizers": db.query(OrganizerApplication)
                .filter(OrganizerApplication.verification_status == "UNDER_REVIEW").count(),
            "approved_organizers": db.query(OrganizerProfile)
                .filter(OrganizerProfile.verification_status == "APPROVED").count(),
            "total_events": len(events),
            "active_events": active,
            "ended_events": sum(1 for lc in lifecycles if lc == "ENDED"),
            "cancelled_events": sum(
                1 for e in events if str(getattr(e.status, "value", e.status)) == "CANCELLED"),
            "published_events": sum(
                1 for e in events
                if str(getattr(e.status, "value", e.status)) in now_active_statuses),
            "pending_events": db.query(Event).filter(Event.status == "PENDING_REVIEW").count(),
            "tickets_sold": db.query(Registration).filter(Registration.status == "CONFIRMED").count(),
            "total_attendees": db.query(Ticket).filter(Ticket.status == "USED").count(),
            "transaction_volume": round(float(volume), 2),
            "wallet_available_total": round(sum(float(w.available_balance or 0) for w in wallets), 2),
            "wallet_pending_total": round(sum(float(w.pending_balance or 0) for w in wallets), 2),
            "pending_withdrawals": len(pending_wd),
            "pending_withdrawal_amount": round(sum(float(w.requested_amount or 0) for w in pending_wd), 2),
            "completed_withdrawals": round(float(paid_wd), 2),
            "total_reviews": db.query(EventReview).count(),
            "open_reports": db.query(Report).filter(Report.status == "OPEN").count(),
        },
    }


@api_router.get("/events", response_model=dict)
def admin_events(admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    from app.services.lifecycle import serialize_event

    events = db.query(Event).order_by(Event.start_date.desc()).all()
    return {"success": True, "items": [serialize_event(e, db) for e in events],
            "message": "Events retrieved"}


@api_router.patch("/events/{event_id}/approve", response_model=dict)
def approve_event(event_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.status = "APPROVED"
    db.add(AuditLog(admin_user_id=admin.id, action="APPROVE_EVENT",
                    entity_type="event", entity_id=event_id, details={"status": "APPROVED"}))
    db.commit()
    return {"success": True, "message": "Event approved"}


@api_router.patch("/events/{event_id}/reject", response_model=dict)
def reject_event(event_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.status = "REJECTED"
    db.add(AuditLog(admin_user_id=admin.id, action="REJECT_EVENT",
                    entity_type="event", entity_id=event_id, details={"status": "REJECTED"}))
    db.commit()
    return {"success": True, "message": "Event rejected"}


@api_router.get("/payments", response_model=dict)
def admin_payments(provider: str | None = None, status: str | None = None,
                   admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    q = db.query(Payment).order_by(Payment.created_at.desc())
    if provider:
        q = q.filter(Payment.provider == provider.upper())
    if status:
        q = q.filter(Payment.status == status.upper())
    rows = q.limit(200).all()
    volume = (
        db.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(Payment.status == PaymentStatus.COMPLETED).scalar() or 0.0
    )
    return {"success": True, "volume": round(float(volume), 2), "items": [
        {"id": p.id, "registration_id": p.registration_id,
         "provider": str(getattr(p.provider, "value", p.provider)),
         "transaction_id": p.transaction_id, "amount": p.amount, "currency": p.currency,
         "status": str(getattr(p.status, "value", p.status)), "created_at": p.created_at}
        for p in rows]}


@api_router.get("/wallets", response_model=dict)
def admin_wallets(admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    rows = []
    for w in db.query(Wallet).all():
        org = db.query(OrganizerProfile).filter(OrganizerProfile.id == w.organizer_id).first()
        user = db.query(UserModel).filter(UserModel.id == org.user_id).first() if org else None
        rows.append({"wallet_id": w.id, "organizer_id": w.organizer_id,
                     "organization_name": org.organization_name if org else None,
                     "organizer_email": user.email if user else None,
                     "available_balance": w.available_balance, "pending_balance": w.pending_balance})
    return {"success": True, "items": rows}


@api_router.get("/settings", response_model=dict)
def get_settings(admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(PlatformSetting).all()
    return {"success": True, "data": {r.key: r.value for r in rows}}


@api_router.patch("/settings", response_model=dict)
def update_settings(payload: dict, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    key = (payload.get("key") or "").strip()
    if key not in EDITABLE_SETTINGS:
        raise HTTPException(status_code=400, detail=f"Editable keys: {sorted(EDITABLE_SETTINGS)}")
    try:
        value = EDITABLE_SETTINGS[key](payload.get("value"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid value")
    if key in ("withdrawal_service_fee", "platform_ticket_fee") and value < 0:
        raise HTTPException(status_code=400, detail="Fee cannot be negative")
    if key == "settlement_hold_days" and value < 0:
        raise HTTPException(status_code=400, detail="Hold days cannot be negative")
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if not row:
        row = PlatformSetting(key=key, value=str(value))
        db.add(row)
    else:
        row.value = str(value)
    db.add(AuditLog(admin_user_id=admin.id, action="UPDATE_SETTING",
                    entity_type="platform_setting", entity_id=None,
                    details={"key": key, "value": str(value)}))
    db.commit()
    return {"success": True, "message": f"{key} updated to {value}"}


@api_router.get("/reports", response_model=dict)
def list_reports(admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return {"success": True, "items": [
        {"id": r.id, "report_type": r.report_type, "reference_type": r.reference_type,
         "reference_id": r.reference_id, "reason": r.reason, "status": r.status, "created_at": r.created_at}
        for r in reports]}


@api_router.patch("/reports/{report_id}/resolve", response_model=dict)
def resolve_report(report_id: int, admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = "RESOLVED"
    report.resolved_by_admin_id = admin.id
    db.commit()
    return {"success": True, "message": "Report resolved"}


@api_router.get("/audit-logs", response_model=dict)
def audit_logs(admin: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    result = []
    for log in logs:
        admin_user = db.query(UserModel).filter(UserModel.id == log.admin_user_id).first()
        result.append({"id": log.id, "action": log.action, "entity_type": log.entity_type,
                       "entity_id": log.entity_id, "details": log.details, "ip_address": log.ip_address,
                       "admin_name": admin_user.username if admin_user else None, "created_at": log.created_at})
    return {"success": True, "items": result}
