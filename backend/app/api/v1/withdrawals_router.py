"""Withdrawals — Phase 7 (request → admin manual payout → exact ledger).

Money never moves automatically. Only the PAID transition touches the wallet,
and only by the exact requested amount through a WITHDRAWAL ledger row —
balances are never zeroed or overwritten.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import rate_limit, require_admin, require_approved_organizer
from app.database import get_db
from app.models.finance import (
    WalletTransaction,
    WalletTxType,
    WithdrawalRequest,
    WithdrawalStatus,
)
from app.models.finance import PaymentProvider as ProviderEnum
from app.models.organizer import OrganizerProfile
from app.models.other import AuditLog
from app.models.user import User as UserModel
from app.services.wallet import ensure_wallet, get_wallet_view, platform_value

api_router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])


def _serialize(w: WithdrawalRequest, db: Session) -> dict:
    org = db.query(OrganizerProfile).filter(OrganizerProfile.id == w.organizer_id).first()
    user = db.query(UserModel).filter(UserModel.id == org.user_id).first() if org else None
    return {
        "id": w.id,
        "organizer_id": w.organizer_id,
        "organization_name": org.organization_name if org else None,
        "organizer_email": user.email if user else None,
        "provider": str(getattr(w.provider, "value", w.provider)),
        "account_number": w.account_number,
        "requested_amount": w.requested_amount,
        "service_fee": w.service_fee,
        "payout_amount": w.payout_amount,
        "status": str(getattr(w.status, "value", w.status)),
        "admin_note": w.admin_note,
        "transaction_reference": w.transaction_reference,
        "created_at": w.created_at,
        "processed_at": w.processed_at,
    }


def _pending_total(db: Session, wallet_id: int) -> float:
    rows = (
        db.query(WithdrawalRequest)
        .filter(WithdrawalRequest.wallet_id == wallet_id,
                WithdrawalRequest.status.in_(["PENDING", "APPROVED"]))
        .all()
    )
    return round(sum(float(r.requested_amount or 0) for r in rows), 2)


@api_router.post("", response_model=dict, dependencies=[Depends(rate_limit(20, 60))])
def request_withdrawal(payload: dict, org: OrganizerProfile = Depends(require_approved_organizer),
                       db: Session = Depends(get_db)):
    provider = (payload.get("provider") or "").upper()
    if provider not in ("ESEWA", "KHALTI"):
        raise HTTPException(status_code=400, detail="provider must be eSewa or Khalti")
    account = (payload.get("account_number") or "").strip()
    if not account:
        raise HTTPException(status_code=400, detail="Wallet/phone number is required")
    try:
        amount = round(float(payload.get("amount")), 2)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid amount")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    view = get_wallet_view(db, org.id)  # opportunistically settles matured funds
    available = float(view["available_balance"] or 0.0)
    wallet = ensure_wallet(db, org.id)
    committed = _pending_total(db, wallet.id)
    if amount > round(available - committed, 2):
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient available balance (Rs.{available}, Rs.{committed} already requested)",
        )
    fee = round(platform_value(db, "withdrawal_service_fee", 20.0), 2)
    if amount <= fee:
        raise HTTPException(status_code=400, detail=f"Amount must exceed the Rs.{fee} service fee")
    req = WithdrawalRequest(
        organizer_id=org.id, wallet_id=wallet.id, provider=ProviderEnum[provider],
        account_number=account, requested_amount=amount, service_fee=fee,
        payout_amount=round(amount - fee, 2), status=WithdrawalStatus.PENDING,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"success": True, "message": "Withdrawal requested. Admin will pay manually.",
            "data": _serialize(req, db)}


@api_router.get("/me", response_model=dict)
def my_withdrawals(org: OrganizerProfile = Depends(require_approved_organizer),
                   db: Session = Depends(get_db)):
    rows = (
        db.query(WithdrawalRequest)
        .filter(WithdrawalRequest.organizer_id == org.id)
        .order_by(WithdrawalRequest.created_at.desc())
        .all()
    )
    return {"success": True, "items": [_serialize(r, db) for r in rows]}


@api_router.get("", response_model=dict)
def list_withdrawals(status: str | None = None, admin: UserModel = Depends(require_admin),
                     db: Session = Depends(get_db)):
    q = db.query(WithdrawalRequest).order_by(WithdrawalRequest.created_at.desc())
    if status:
        q = q.filter(WithdrawalRequest.status == status.upper())
    return {"success": True, "items": [_serialize(r, db) for r in q.all()]}


@api_router.post("/{withdrawal_id}/approve", response_model=dict)
def approve_withdrawal(withdrawal_id: int, admin: UserModel = Depends(require_admin),
                       db: Session = Depends(get_db)):
    req = db.query(WithdrawalRequest).filter(WithdrawalRequest.id == withdrawal_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    if str(getattr(req.status, "value", req.status)) != "PENDING":
        raise HTTPException(status_code=400, detail="Only PENDING withdrawals can be approved")
    req.status = WithdrawalStatus.APPROVED
    db.add(AuditLog(admin_user_id=admin.id, action="WITHDRAWAL_APPROVE",
                    entity_type="withdrawal", entity_id=req.id, details={}))
    db.commit()
    return {"success": True, "message": "Withdrawal approved. Pay manually, then confirm with the transaction reference."}


@api_router.post("/{withdrawal_id}/pay", response_model=dict)
def confirm_payout(withdrawal_id: int, payload: dict, admin: UserModel = Depends(require_admin),
                   db: Session = Depends(get_db)):
    """Admin confirms the MANUAL payment: deducts the exact amount via ledger."""
    req = db.query(WithdrawalRequest).filter(WithdrawalRequest.id == withdrawal_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    if str(getattr(req.status, "value", req.status)) not in ("PENDING", "APPROVED"):
        raise HTTPException(status_code=400, detail="Withdrawal is already processed")
    reference = (payload.get("transaction_reference") or "").strip()
    if not reference:
        raise HTTPException(status_code=400, detail="transaction_reference is required")

    view = get_wallet_view(db, req.organizer_id)
    wallet = ensure_wallet(db, req.organizer_id)
    if float(view["available_balance"] or 0.0) < float(req.requested_amount or 0):
        raise HTTPException(status_code=400, detail="Organizer balance no longer covers this withdrawal")

    amount = round(float(req.requested_amount), 2)
    db.add(WalletTransaction(
        wallet_id=wallet.id, type=WalletTxType.WITHDRAWAL, amount=-amount,
        reference_type="WITHDRAWAL", reference_id=req.id,
        description=f"Manual payout Rs.{amount:.2f} to {req.account_number} (ref {reference})",
    ))
    wallet.available_balance = round(float(wallet.available_balance or 0.0) - amount, 2)
    req.status = WithdrawalStatus.PAID
    req.transaction_reference = reference
    req.admin_note = payload.get("admin_note")
    req.processed_at = datetime.utcnow()
    db.add(AuditLog(admin_user_id=admin.id, action="WITHDRAWAL_PAID",
                    entity_type="withdrawal", entity_id=req.id,
                    details={"amount": amount, "reference": reference}))
    db.commit()
    db.refresh(req)
    return {"success": True, "message": f"Paid Rs.{req.payout_amount} to organizer (fee Rs.{req.service_fee}).",
            "data": _serialize(req, db)}


@api_router.post("/{withdrawal_id}/reject", response_model=dict)
def reject_withdrawal(withdrawal_id: int, payload: dict, admin: UserModel = Depends(require_admin),
                      db: Session = Depends(get_db)):
    req = db.query(WithdrawalRequest).filter(WithdrawalRequest.id == withdrawal_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    if str(getattr(req.status, "value", req.status)) not in ("PENDING", "APPROVED"):
        raise HTTPException(status_code=400, detail="Withdrawal is already processed")
    reason = (payload.get("admin_note") or payload.get("reason") or "").strip()
    if not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    req.status = WithdrawalStatus.REJECTED
    req.admin_note = reason
    req.processed_at = datetime.utcnow()
    db.add(AuditLog(admin_user_id=admin.id, action="WITHDRAWAL_REJECT",
                    entity_type="withdrawal", entity_id=req.id, details={"reason": reason}))
    db.commit()
    return {"success": True, "message": "Withdrawal rejected"}
