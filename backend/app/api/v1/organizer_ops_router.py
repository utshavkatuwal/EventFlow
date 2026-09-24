"""Organizer operations — Phase 6 (attendees, hardened scan, sales, wallet).

All routes require an APPROVED organizer who owns the event. Attendance can
only change through the scan endpoint — never by arbitrary client writes.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import rate_limit, require_approved_organizer
from app.database import get_db
from app.models.event import Event
from app.models.organizer import OrganizerProfile
from app.models.ticket import Registration, Ticket, TicketScan, TicketType
from app.models.user import User as UserModel
from app.services.lifecycle import serialize_event
from app.services.wallet import get_wallet_view, settle_due

api_router = APIRouter(prefix="/organizer", tags=["OrganizerOps"])


def _own_event(event_id: int, org: OrganizerProfile, db: Session) -> Event:
    try:
        event_id = int(event_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid event_id")
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    if ev.organizer_id != org.id:
        raise HTTPException(status_code=403, detail="Not your event")
    return ev


def _attendee_rows(ev: Event, db: Session) -> tuple[list[dict], dict]:
    regs = (
        db.query(Registration)
        .filter(Registration.event_id == ev.id, Registration.status != "CANCELLED")
        .order_by(Registration.registration_date.desc())
        .all()
    )
    rows = []
    attended = 0
    revenue = 0.0
    for r in regs:
        ticket = db.query(Ticket).filter(Ticket.registration_id == r.id).first()
        user = db.query(UserModel).filter(UserModel.id == r.user_id).first()
        tt = db.query(TicketType).filter(TicketType.id == r.ticket_type_id).first()
        tstatus = str(getattr(ticket.status, "value", ticket.status)) if ticket else "NONE"
        if tstatus == "USED":
            attended += 1
        if str(getattr(r.status, "value", r.status)) == "CONFIRMED":
            revenue = round(revenue + float(r.amount_paid or 0.0), 2)
        rows.append({
            "registration_id": r.id,
            "attendee_name": (
                f"{user.first_name or ''} {user.last_name or ''}".strip()
                or (user.username if user else "-")
            ),
            "attendee_email": user.email if user else None,
            "ticket_id": ticket.id if ticket else None,
            "ticket_code": ticket.ticket_code if ticket else None,
            "ticket_type": tt.name if tt else None,
            "registration_date": r.registration_date,
            "registration_status": str(getattr(r.status, "value", r.status)),
            "payment_status": str(getattr(r.payment_status, "value", r.payment_status)),
            "amount_paid": r.amount_paid,
            "attendance_status": tstatus,
            "attendance_time": ticket.checked_in_at if ticket else None,
        })
    sold = sum(1 for r in regs if str(getattr(r.status, "value", r.status)) == "CONFIRMED")
    valid = sum(1 for row in rows if row["attendance_status"] == "VALID")
    stats = {
        "tickets_sold": sold,
        "tickets_remaining": max((ev.max_capacity or 0) - sold, 0),
        "attended": attended,
        "not_attended": valid,
        "revenue": revenue,
    }
    return rows, stats


@api_router.get("/events/{event_id}/attendees", response_model=dict)
def event_attendees(event_id: int, org: OrganizerProfile = Depends(require_approved_organizer),
                    db: Session = Depends(get_db)):
    ev = _own_event(event_id, org, db)
    rows, stats = _attendee_rows(ev, db)
    return {"success": True, "data": {"event": serialize_event(ev, db), "attendees": rows, "stats": stats}}


@api_router.get("/events/{event_id}/sales", response_model=dict)
def event_sales(event_id: int, org: OrganizerProfile = Depends(require_approved_organizer),
                db: Session = Depends(get_db)):
    from app.models.finance import WalletTransaction, WalletTxType

    ev = _own_event(event_id, org, db)
    tts = db.query(TicketType).filter(TicketType.event_id == ev.id).all()
    breakdown = []
    gross = 0.0
    for tt in tts:
        sold = int(tt.sold_count or 0)
        line = round(sold * float(tt.price or 0.0), 2)
        gross = round(gross + line, 2)
        breakdown.append({"ticket_type": tt.name, "price": tt.price, "capacity": tt.capacity,
                          "sold": sold, "remaining": max((tt.capacity or 0) - sold, 0), "gross": line})
    wallet = get_wallet_view(db, org.id)
    fee_rows = (
        db.query(func.coalesce(func.sum(WalletTransaction.amount), 0.0))
        .join(Registration, Registration.id == WalletTransaction.reference_id)
        .filter(WalletTransaction.reference_type == "REGISTRATION",
                WalletTransaction.type == WalletTxType.PLATFORM_FEE,
                Registration.event_id == ev.id)
        .scalar()
        or 0.0
    )
    return {"success": True, "data": {
        "event": serialize_event(ev, db), "breakdown": breakdown,
        "gross_revenue": gross, "platform_fees": round(abs(float(fee_rows)), 2),
        "net_earning": round(gross - abs(float(fee_rows)), 2),
        "wallet": {"available_balance": wallet["available_balance"],
                   "pending_balance": wallet["pending_balance"]},
    }}


SCAN_ERRORS = {
    "INVALID_TICKET", "WRONG_EVENT", "NOT_CONFIRMED", "NOT_PAID",
    "TICKET_CANCELLED", "TICKET_EXPIRED", "ALREADY_USED",
}


def _scan(db: Session, *, qr_token: str, event_id: int | None,
          scanner: OrganizerProfile) -> dict:
    token = (qr_token or "").strip()
    if not token:
        raise HTTPException(status_code=400, detail={"valid": False, "error": "INVALID_TICKET",
                                                     "message": "QR token required"})
    ticket = db.query(Ticket).filter(Ticket.qr_token == token).first()
    if not ticket:
        # allow ticket-code fallback (manual entry)
        ticket = db.query(Ticket).filter(Ticket.ticket_code == token).first()
    if not ticket:
        raise HTTPException(status_code=404, detail={"valid": False, "error": "INVALID_TICKET",
                                                     "message": "This ticket could not be verified."})
    from app.models.ticket import Registration as RegModel

    reg = db.query(RegModel).filter(RegModel.id == ticket.registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail={"valid": False, "error": "INVALID_TICKET",
                                                     "message": "This ticket could not be verified."})
    ev = db.query(Event).filter(Event.id == reg.event_id).first()
    if event_id is not None and ev and ev.id != int(event_id):
        raise HTTPException(status_code=400, detail={"valid": False, "error": "WRONG_EVENT",
                                                     "message": "Ticket belongs to a different event."})
    if not ev or ev.organizer_id != scanner.id:
        raise HTTPException(status_code=403, detail={"valid": False, "error": "WRONG_EVENT",
                                                     "message": "You are not the organizer of this event."})
    if str(getattr(reg.status, "value", reg.status)) != "CONFIRMED":
        raise HTTPException(status_code=400, detail={"valid": False, "error": "NOT_CONFIRMED",
                                                     "message": "Order is not confirmed (payment pending)."})
    if str(getattr(reg.payment_status, "value", reg.payment_status)) != "PAID":
        raise HTTPException(status_code=400, detail={"valid": False, "error": "NOT_PAID",
                                                     "message": "Ticket is not paid."})
    tstatus = str(getattr(ticket.status, "value", ticket.status))
    user = db.query(UserModel).filter(UserModel.id == reg.user_id).first()
    info = {"attendee": (
                f"{user.first_name or ''} {user.last_name or ''}".strip()
                or (user.username if user else "-")),
            "event": ev.title, "ticket_id": ticket.id, "ticket_code": ticket.ticket_code}
    if tstatus == "CANCELLED":
        raise HTTPException(status_code=400, detail={"valid": False, "error": "TICKET_CANCELLED",
                                                     **info, "message": "This ticket has been cancelled."})
    if tstatus == "EXPIRED":
        raise HTTPException(status_code=400, detail={"valid": False, "error": "TICKET_EXPIRED",
                                                     **info, "message": "This ticket has expired."})
    if tstatus == "USED":
        db.add(TicketScan(ticket_id=ticket.id, scanned_by_user_id=scanner.user_id,
                          result="ALREADY_USED", notes="Rescan attempt"))
        db.commit()
        raise HTTPException(status_code=400, detail={"valid": False, "error": "ALREADY_USED",
                                                     **info, "message": "TICKET ALREADY USED",
                                                     "checked_in_at": ticket.checked_in_at.isoformat()
                                                     if ticket.checked_in_at else None})
    ticket.status = "USED"
    ticket.checked_in_at = datetime.utcnow()
    db.add(TicketScan(ticket_id=ticket.id, scanned_by_user_id=scanner.user_id, result="SUCCESS"))
    db.commit()
    return {"valid": True, "message": "ATTENDANCE CONFIRMED", **info,
            "checked_in_at": ticket.checked_in_at.isoformat()}


@api_router.post("/scan", response_model=dict, dependencies=[Depends(rate_limit(120, 60))])
def scan_ticket(payload: dict, org: OrganizerProfile = Depends(require_approved_organizer),
                db: Session = Depends(get_db)):
    try:
        result = _scan(db, qr_token=payload.get("qr_token"), event_id=payload.get("event_id"), scanner=org)
    except HTTPException as e:
        # normalize scan failures to 200 envelope? No — keep HTTP errors, frontend reads detail.
        raise e
    return {"success": True, "message": result["message"], "data": result}


@api_router.get("/wallet", response_model=dict)
def organizer_wallet(org: OrganizerProfile = Depends(require_approved_organizer),
                     db: Session = Depends(get_db)):
    return {"success": True, "data": get_wallet_view(db, org.id)}


@api_router.post("/wallet/settle", response_model=dict)
def settle_wallet(org: OrganizerProfile = Depends(require_approved_organizer),
                  db: Session = Depends(get_db)):
    return {"success": True, "message": "Settlement processed", "data": settle_due(db, org.id)}
