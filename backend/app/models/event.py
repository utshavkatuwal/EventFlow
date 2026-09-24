from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organizer_id = Column(Integer, ForeignKey("organizer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("event_categories.id", ondelete="SET NULL"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(280), nullable=False, unique=True, index=True)
    short_description = Column(String(500), nullable=True)
    full_description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    venue = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Nepal", nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    max_capacity = Column(Integer, nullable=False, default=100)
    status = Column(SAEnum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    price_min = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class EventCategory(Base):
    __tablename__ = "event_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(120), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    icon = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
