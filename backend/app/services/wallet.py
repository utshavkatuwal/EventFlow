"""Organizer wallet ledger — every balance move has a row (Phase 5).

On paid confirmation:  TICKET_SALE +gross and PLATFORM_FEE −fee hit
pending_balance (net = organizer earning, held for settlement).
`available + pending` always equals the sum of non-memo ledger amounts.

Settlement (configurable via platform_settings SETTLEMENT_HOLD_DAYS, default 2):
after an event ends + hold, the registration's net moves pending → available,
marked by an ADJUSTMENT memo row (reference_type SETTLEMENT). Runs
opportunistically on wallet reads + explicit settle endpoint.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.finance import (
    DEFAULT_SETTINGS,
    PlatformSetting,
    Wallet,
    WalletTransaction,
    WalletTxType,
)


def platform_value(db: Session, key: str, default: float) -> float:
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if row:
        try:
            return float(row.value)
        except ValueError:
            pass
    return float(DEFAULT_SETTINGS.get(key, (default, ""))[0] if key in DEFAULT_SETTINGS else default)


def ensure_wallet(db: Session, organizer_id: int) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.organizer_id == organizer_id).first()
    if not wallet:
        wallet = Wallet(organizer_id=organizer_id, available_balance=0.0, pending_balance=0.0)
        db.add(wallet)
        db.flush()
    return wallet


def _ledger(db: Session, wallet: Wallet, kind: WalletTxType, amount: float,
            ref_type: str | None, ref_id: int | None, desc: str) -> None:
    db.add(WalletTransaction(
        wallet_id=wallet.id, type=kind, amount=amount,
        reference_type=ref_type, reference_id=ref_id, description=desc,
    ))


def record_ticket_sale(db: Session, *, organizer_id: int, registration_id: int, gross: float,
                       commit: bool = True) -> dict:
    """Ledger for one CONFIRMED paid ticket. Idempotent per registration."""
    from app.models.finance import WalletTransaction as WT

    wallet = ensure_wallet(db, organizer_id)
    exists = (
        db.query(WT)
        .filter(WT.wallet_id == wallet.id, WT.type == WalletTxType.TICKET_SALE,
                WT.reference_type == "REGISTRATION", WT.reference_id == registration_id)
        .first()
    )
    if exists:
        return {"wallet": wallet, "already": True}
    fee = platform_value(db, "platform_ticket_fee", 20.0)
    fee = max(min(fee, gross), 0.0)
    net = round(gross - fee, 2)
    _ledger(db, wallet, WalletTxType.TICKET_SALE, round(gross, 2),
            "REGISTRATION", registration_id, f"Ticket sale Rs.{gross:.2f} (registration {registration_id})")
    if fee > 0:
        _ledger(db, wallet, WalletTxType.PLATFORM_FEE, round(-fee, 2),
                "REGISTRATION", registration_id, f"Platform fee Rs.{fee:.2f}")
    wallet.pending_balance = round((wallet.pending_balance or 0.0) + net, 2)
    if commit:
        db.commit()
    else:
        db.flush()
    return {"wallet": wallet, "already": False, "net": net, "fee": fee}


def settle_due(db: Session, organizer_id: int | None = None) -> dict:
    """Move matured pending funds to available. Returns totals settled."""
    from app.models.event import Event
    from app.models.ticket import Registration

    hold_days = int(platform_value(db, "settlement_hold_days", 2))
    cutoff = datetime.utcnow() - timedelta(days=hold_days)
    wallets = db.query(Wallet)
    if organizer_id is not None:
        # organizer_id here is the organizer_profiles.id
        wallets = wallets.filter(Wallet.organizer_id == organizer_id)
    settled = 0
    total = 0.0
    for wallet in wallets.all():
        regs = (
            db.query(Registration)
            .join(Event, Event.id == Registration.event_id)
            .filter(
                Registration.status == "CONFIRMED",
                Registration.payment_status == "PAID",
                Registration.amount_paid > 0,
                Event.organizer_id == wallet.organizer_id,
                Event.end_date.isnot(None),
                Event.end_date <= cutoff,
            )
            .all()
        )
        for reg in regs:
            already = (
                db.query(WalletTransaction)
                .filter(WalletTransaction.wallet_id == wallet.id,
                        WalletTransaction.reference_type == "SETTLEMENT",
                        WalletTransaction.reference_id == reg.id)
                .first()
            )
            if already:
                continue
            sale = (
                db.query(WalletTransaction)
                .filter(WalletTransaction.wallet_id == wallet.id,
                        WalletTransaction.type == WalletTxType.TICKET_SALE,
                        WalletTransaction.reference_type == "REGISTRATION",
                        WalletTransaction.reference_id == reg.id)
                .first()
            )
            if not sale:
                continue
            fee_row = (
                db.query(WalletTransaction)
                .filter(WalletTransaction.wallet_id == wallet.id,
                        WalletTransaction.type == WalletTxType.PLATFORM_FEE,
                        WalletTransaction.reference_type == "REGISTRATION",
                        WalletTransaction.reference_id == reg.id)
                .first()
            )
            net = round(sale.amount + (fee_row.amount if fee_row else 0.0), 2)
            if net <= 0:
                continue
            _ledger(db, wallet, WalletTxType.ADJUSTMENT, 0.0,
                    "SETTLEMENT", reg.id, f"Settled Rs.{net:.2f} to available (registration {reg.id})")
            wallet.pending_balance = round((wallet.pending_balance or 0.0) - net, 2)
            wallet.available_balance = round((wallet.available_balance or 0.0) + net, 2)
            settled += 1
            total = round(total + net, 2)
    if settled:
        db.commit()
    return {"settled_count": settled, "settled_amount": total}


def get_wallet_view(db: Session, organizer_id: int) -> dict:
    settle_due(db, organizer_id)
    wallet = ensure_wallet(db, organizer_id)
    db.refresh(wallet)
    txns = (
        db.query(WalletTransaction)
        .filter(WalletTransaction.wallet_id == wallet.id)
        .order_by(WalletTransaction.created_at.desc())
        .limit(50)
        .all()
    )
    return {
        "available_balance": wallet.available_balance,
        "pending_balance": wallet.pending_balance,
        "transactions": [
            {"id": t.id, "type": str(getattr(t.type, "value", t.type)), "amount": t.amount,
             "reference_type": t.reference_type, "reference_id": t.reference_id,
             "description": t.description, "created_at": t.created_at}
            for t in txns
        ],
    }
