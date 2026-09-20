# EventFlow - Backend Documentation

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── core/
│   │   ├── config.py        # Settings management
│   │   └── security.py      # Auth utilities (JWT, bcrypt)
│   ├── database/
│   │   └── __init__.py      # DB connection, session, Base
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py          # User, Role, Permission, UserRole
│   │   ├── event.py         # Event, EventCategory
│   │   ├── organizer.py     # OrganizerProfile
│   │   ├── event_image.py   # EventImage
│   │   ├── ticket.py        # TicketType, Registration, Ticket, TicketScan
│   │   └── other.py         # Review, Favorite, Notification, Report, AuditLog
│   ├── schemas/             # Pydantic validation schemas
│   │   └── __init__.py      # Request/response models
│   ├── api/
│   │   └── v1/              # API version 1
│   │       ├── router.py    # Main router aggregator
│   │       ├── auth_router.py        # Auth endpoints
│   │       ├── events_router.py      # Event CRUD, search, stats
│   │       ├── events_create_router.py # Event creation
│   │       ├── categories_router.py  # Category management
│   │       ├── user_router.py        # User dashboard data
│   │       ├── user_profile_router.py # User profile
│   │       ├── tickets_router.py     # Ticket retrieval
│   │       ├── reviews_router.py     # Event reviews
│   │       ├── notifications_router.py # Notifications
│   │       ├── search_router.py      # Event search
│   │       ├── admin_router.py       # Admin operations
│   │       ├── organizers_router.py  # Organizer management
│   │       ├── users_router.py       # User management (admin)
│   │       └── organizer_profile_router.py # Organizer profile
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py  # Registration, login, tokens, QR
│   │   ├── event_service.py # Event operations, seeding
│   │   ├── analytics_service.py # Dashboard statistics
│   │   ├── public_service.py # Public queries
│   │   ├── file_service.py  # File upload handling
│   │   └── file_utils.py    # Filename utilities
│   ├── auth/
│   │   └── dependencies.py  # Auth dependencies
│   └── utils/               # Shared utilities
├── tests/                   # Backend tests
│   ├── test_api.py          # General API tests
│   ├── test_auth.py         # Auth tests
│   ├── test_integration.py  # Integration tests
│   └── test_new_routes.py   # New route tests
├── scripts/
│   └── seed.py              # Database seeding
├── requirements.txt         # Python dependencies
└── README.md
```

## Key Technologies

- FastAPI for REST API
- SQLAlchemy 2.0 for ORM
- Pydantic for validation
- JWT for authentication (access + refresh tokens)
- bcrypt for password hashing
- Alembic for migrations
- MySQL 8.0 database

## API Design

- RESTful endpoints
- Versioned at `/api/v1/`
- Consistent JSON response format
- Proper HTTP status codes
- Pagination on list endpoints

## Database

18 tables with proper relationships:
- users, roles, permissions, user_roles, role_permissions
- organizer_profiles
- event_categories, events, event_images
- ticket_types, registrations, tickets, ticket_scans
- event_reviews, favorites, notifications
- reports, audit_logs

## Authentication Flow

1. Register → bcrypt hash password
2. Login → JWT access (30min) + refresh (7 days) tokens
3. Each request: Authorization: Bearer <token>
4. Server validates token, extracts user_id
5. Role checks performed server-side

## Running Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

## Testing

```bash
pytest tests/ -v
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc