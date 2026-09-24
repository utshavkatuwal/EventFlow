"""Organizer verification models (Phase 1): applications + secure documents."""
from __future__ import annotations

import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.database import Base


class VerificationStatus(str, enum.Enum):
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class OrganizerApplication(Base):
    """One application per organizer user (resubmission updates the row)."""

    __tablename__ = "organizer_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    organization_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    verification_info = Column(Text, nullable=True)
    verification_status = Column(
        SAEnum(VerificationStatus),
        nullable=False,
        default=VerificationStatus.UNDER_REVIEW,
        index=True,
    )
    rejection_reason = Column(Text, nullable=True)
    submitted_at = Column(DateTime, server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by_admin_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class OrganizerDocument(Base):
    """Verification files. Served ONLY via backend — never a public static dir."""

    __tablename__ = "organizer_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id = Column(
        Integer,
        ForeignKey("organizer_applications.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    stored_path = Column(String(500), nullable=False)
    mime_type = Column(String(120), nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
