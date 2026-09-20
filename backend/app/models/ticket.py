from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base
import enum


class TicketStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SOLD_OUT = "SOLD_OUT"


class TicketType(Base):
    __tablename__ = "ticket_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="NPR", nullable=False)
    capacity = Column(Integer, nullable=False, default=100)
    sold_count = Column(Integer, default=0, nullable=False)
    sale_start = Column(DateTime, nullable=True)
    sale_end = Column(DateTime, nullable=True)
    status = Column(SAEnum(TicketStatus), default=TicketStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class RegistrationStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    WAITLISTED = "WAITLISTED"


class PaymentStatus(str, enum.Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id", ondelete="SET NULL"), nullable=False)
    registration_date = Column(DateTime, server_default=func.now(), nullable=False)
    status = Column(SAEnum(RegistrationStatus), default=RegistrationStatus.CONFIRMED, nullable=False)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.UNPAID, nullable=False)
    amount_paid = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', 'ticket_type_id', name='uq_registration_event_user_ticket'),
    )


class TicketStatusValid(str, enum.Enum):
    VALID = "VALID"
    USED = "USED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id", ondelete="SET NULL"), nullable=False)
    ticket_code = Column(String(100), nullable=False, unique=True, index=True)
    qr_token = Column(String(255), nullable=False, unique=True, index=True)
    qr_code_url = Column(String(500), nullable=True)
    status = Column(SAEnum(TicketStatusValid), default=TicketStatusValid.VALID, nullable=False)
    checked_in_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class TicketScan(Base):
    __tablename__ = "ticket_scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    scanned_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    scanned_at = Column(DateTime, server_default=func.now(), nullable=False)
    result = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
