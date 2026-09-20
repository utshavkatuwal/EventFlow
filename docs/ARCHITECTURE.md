# Architecture

## Overview

EventFlow follows a modular monolith architecture with clean separation between frontend and backend.

## Frontend

- **Framework**: React 18 + Vite
- **Routing**: React Router v6
- **Styling**: CSS Modules with global design system variables
- **State**: React Context for auth, API client, and navigation
- **HTTP**: Axios with interceptors for auth token injection

## Backend

- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy 2.0 with MySQL backend
- **Migrations**: Alembic
- **Auth**: JWT (access + refresh tokens)
- **Architecture**: Repository pattern with service layer

### Module Structure

```
app/
├── core/          # Configuration, security utilities
├── config/        # Settings management
├── database/      # Connection, session, models base
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic validation schemas
├── api/
│   └── v1/        # API version 1 routes
│       ├── router.py          # Main router aggregating all sub-routers
│       ├── events_router.py   # Event CRUD, search, filtering
│       ├── categories_router.py
│       ├── user_router.py     # User profile, dashboard stats
│       ├── tickets_router.py  # Ticket retrieval
│       ├── reviews_router.py
│       ├── notifications_router.py
│       ├── search_router.py
│       ├── admin_router.py    # Admin operations
│       ├── organizers_router.py
│       └── users_router.py    # User management (admin)
├── services/      # Business logic layer
├── repositories/  # Data access layer
├── auth/          # Authentication utilities
└── utils/         # Shared utilities
```

## Database

- **Engine**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **Design**: Normalized relational schema with proper foreign keys, indexes, and constraints
- **Migrations**: Alembic with versioned migration files

## Authentication Flow

1. User registers → password hashed with bcrypt → stored in DB
2. User logs in → JWT access token (30 min) + refresh token (7 days) issued
3. Frontend stores tokens in localStorage
4. Each API request includes Bearer token
5. Server validates token on each request

## API Design Principles

- RESTful conventions
- Versioned URLs (`/api/v1/`)
- Consistent JSON response format
- Proper HTTP status codes
- Pagination on list endpoints

## Future Flutter Integration

The REST API is designed to be consumed by any client:
- All endpoints use standard HTTP methods
- JSON request/response format
- Token-based authentication
- No frontend-specific logic in backend

Key endpoints for Flutter:
- `POST /api/v1/auth/login`
- `GET /api/v1/events`
- `GET /api/v1/events/{id}`
- `POST /api/v1/events/{id}/register`
- `GET /api/v1/users/me/tickets`
- `POST /api/v1/checkins/verify`
