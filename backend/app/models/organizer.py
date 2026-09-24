from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class OrganizerProfile(Base):
    __tablename__ = "organizer_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    organization_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Nepal", nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    # Phase 1 verification workflow: UNDER_REVIEW | APPROVED | REJECTED
    verification_status = Column(String(20), nullable=False, default="UNDER_REVIEW", server_default="UNDER_REVIEW", index=True)
    verification_info = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
