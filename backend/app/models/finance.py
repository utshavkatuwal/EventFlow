"""Finance models: payments, wallets, withdrawals, platform settings (Phase 1)."""
from __future__ import annotations

import enum

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database import Base


class PaymentProvider(str, enum.Enum):
    ESEWA = "ESEWA"
    KHALTI = "KHALTI"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(Base):
    """One row per provider transaction attempt. Idempotency via transaction_id."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_id = Column(
        Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider = Column(SAEnum(PaymentProvider), nullable=False, index=True)
    transaction_id = Column(String(255), nullable=True, unique=True, index=True)
    amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default="NPR")
    status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)
    provider_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organizer_id = Column(
        Integer,
        ForeignKey("organizer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    available_balance = Column(Float, nullable=False, default=0.0)
    pending_balance = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class WalletTxType(str, enum.Enum):
    TICKET_SALE = "TICKET_SALE"
    PLATFORM_FEE = "PLATFORM_FEE"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"
    ADJUSTMENT = "ADJUSTMENT"


class WalletTransaction(Base):
    """Ledger — NEVER change a balance without inserting a row here."""

    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_id = Column(
        Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type = Column(SAEnum(WalletTxType), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    reference_type = Column(String(50), nullable=True, index=True)
    reference_id = Column(Integer, nullable=True, index=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class WithdrawalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PAID = "PAID"
    REJECTED = "REJECTED"


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organizer_id = Column(
        Integer,
        ForeignKey("organizer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    wallet_id = Column(
        Integer, ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    provider = Column(SAEnum(PaymentProvider), nullable=False)
    account_number = Column(String(100), nullable=False)
    requested_amount = Column(Float, nullable=False)
    service_fee = Column(Float, nullable=False, default=20.0)
    payout_amount = Column(Float, nullable=False)
    status = Column(
        SAEnum(WithdrawalStatus), nullable=False, default=WithdrawalStatus.PENDING, index=True
    )
    admin_note = Column(Text, nullable=True)
    transaction_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)


class PlatformSetting(Base):
    """Configurable platform values (service fee etc.). Admin-editable."""

    __tablename__ = "platform_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(String(500), nullable=False)
    description = Column(String(500), nullable=True)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


DEFAULT_SETTINGS = {
    "withdrawal_service_fee": ("20", "Flat demo service fee (NPR) deducted from organizer withdrawals"),
    "platform_ticket_fee": ("20", "Flat demo platform fee (NPR) per paid ticket"),
    "settlement_hold_days": ("2", "Days after event end before pending wallet funds become available"),
}
