from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.event import EventStatus, EventCategory


# Common
class ResponseModel(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20


class PaginationResult(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    total_pages: int


# Auth
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# User
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


# Organizer
class OrganizerCreate(BaseModel):
    organization_name: str
    description: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None


class OrganizerResponse(BaseModel):
    id: int
    user_id: int
    organization_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Category
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Event
class EventCreate(BaseModel):
    title: str
    category_id: int
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_capacity: int = 100
    is_featured: bool = False
    price_min: float = 0.0


class EventUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_capacity: Optional[int] = None
    is_featured: Optional[bool] = None


class EventResponse(BaseModel):
    id: int
    organizer_id: int
    category_id: int
    title: str
    slug: str
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    cover_image_url: Optional[str] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str
    start_date: datetime
    end_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_capacity: int
    status: str
    is_featured: bool
    price_min: float
    organizer_name: Optional[str] = None
    category_name: Optional[str] = None
    total_registrations: Optional[int] = 0
    available_capacity: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Ticket Type
class TicketTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = 0.0
    currency: str = "NPR"
    capacity: int = 100
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None


class TicketTypeResponse(BaseModel):
    id: int
    event_id: int
    name: str
    description: Optional[str] = None
    price: float
    currency: str
    capacity: int
    sold_count: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Registration
class RegistrationRequest(BaseModel):
    event_id: int
    ticket_type_id: int


class RegistrationResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    ticket_type_id: int
    status: str
    payment_status: str
    amount_paid: float
    registration_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Ticket
class TicketResponse(BaseModel):
    id: int
    registration_id: int
    ticket_type_id: int
    ticket_code: str
    qr_token: str
    qr_code_url: Optional[str] = None
    status: str
    checked_in_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Review
class ReviewCreate(BaseModel):
    event_id: int
    registration_id: int
    rating: int
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    registration_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None
    is_reported: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Notification
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
