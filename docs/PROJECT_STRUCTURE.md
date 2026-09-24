# Project Structure

```
EventFlow/
├── frontend/                      # React SPA
│   ├── src/
│   │   ├── components/            # Reusable components
│   │   │   ├── Navbar.jsx
│   │   │   ├── Layout.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── EventCard.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── Loading.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── RequireAuth.jsx
│   │   │   ├── RoleGuard.jsx
│   │   │   ├── RoleHome.jsx
│   │   │   └── ... (27 total: Avatar, Badge, Modal, Table, ...)
│   │   ├── pages/                 # Page components (35 total)
│   │   │   ├── HomePage.jsx
│   │   │   ├── EventsPage.jsx
│   │   │   ├── EventDetailPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── UserDashboardPage.jsx
│   │   │   ├── OrganizerDashboardPage.jsx
│   │   │   ├── AdminDashboardPage.jsx
│   │   │   ├── AdminWithdrawalsPage.jsx
│   │   │   ├── PaymentCallbackPage.jsx
│   │   │   ├── TicketPage.jsx
│   │   │   ├── CheckInPage.jsx
│   │   │   ├── ProfilePage.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── layouts/               # Page layouts
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── services/              # API service layer
│   │   │   ├── api.js
│   │   │   └── saved.js
│   │   ├── utils/
│   │   │   ├── roles.js
│   │   │   ├── images.js
│   │   │   └── ...
│   │   ├── context/               # React Context providers
│   │   │   ├── AuthContext.jsx
│   │   │   ├── ApiContext.jsx
│   │   │   └── NavContext.jsx
│   │   ├── utils/                 # Utility functions
│   │   ├── assets/                # Static assets
│   │   ├── styles/                # Global CSS and design tokens
│   │   │   ├── global.css
│   │   │   └── *.css (per-component styles)
│   │   ├── App.jsx               # Main app with routes
│   │   └── main.jsx              # Entry point
│   ├── public/
│   │   └── images/
│   ├── tests/                     # Frontend tests (vitest)
│   ├── Dockerfile                 # Multi-stage build → nginx
│   ├── nginx.conf                 # SPA fallback + /api/ proxy to backend
│   ├── package.json
│   └── vite.config.js
│
├── backend/                       # FastAPI backend
│   ├── Dockerfile                 # python:3.11-slim + uvicorn
│   ├── .dockerignore
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py               # Lifespan startup, absolute upload mounts
│   │   ├── core/
│   │   │   ├── config.py         # Settings (env-driven, DEBUG=False default)
│   │   │   └── security.py       # Auth utilities
│   │   ├── config/               # Configuration modules
│   │   ├── database/
│   │   │   ├── __init__.py       # Engine/session + ensure_phase1_schema backfill
│   │   │   └── models.py         # Re-exports all models for Base.metadata
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   ├── organizer.py
│   │   │   ├── event_image.py
│   │   │   ├── ticket.py
│   │   │   ├── finance.py        # payments, wallets, withdrawals, platform_settings
│   │   │   ├── verification.py   # organizer_applications, organizer_documents
│   │   │   └── other.py
│   │   ├── schemas/              # Pydantic validation
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   └── v1/               # API version 1
│   │   │       ├── router.py     # Main router
│   │   │       ├── events_router.py
│   │   │       ├── events_create_router.py
│   │   │       ├── categories_router.py
│   │   │       ├── user_router.py
│   │   │       ├── users_router.py
│   │   │       ├── tickets_router.py
│   │   │       ├── registrations_router.py
│   │   │       ├── reviews_router.py
│   │   │       ├── notifications_router.py
│   │   │       ├── search_router.py
│   │   │       ├── admin_router.py
│   │   │       ├── organizers_router.py
│   │   │       ├── organizer_ops_router.py
│   │   │       ├── organizer_profile_router.py
│   │   │       ├── organizer_applications_router.py
│   │   │       ├── payments_router.py
│   │   │       ├── withdrawals_router.py
│   │   │       └── user_profile_router.py
│   │   ├── services/             # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── event_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── booking.py
│   │   │   ├── lifecycle.py
│   │   │   ├── wallet.py
│   │   │   ├── public_service.py
│   │   │   ├── file_service.py
│   │   │   ├── file_utils.py
│   │   │   └── payments/         # esewa.py, khalti.py, base.py
│   │   ├── repositories/         # Data access layer
│   │   ├── auth/
│   │   │   └── dependencies.py
│   │   └── utils/
│   ├── scripts/
│   │   └── seed.py               # Database seeding
│   ├── tests/                    # pytest (conftest isolates test_eventflow.db)
│   ├── docs/
│   ├── requirements.txt
│   └── package.json              # npm-style shortcuts (dev/seed/test)
│
├── database/                      # Database schema & seeds
│   ├── migrations/               # Alembic migrations
│   │   ├── env.py                # Overrides URL from settings.DATABASE_URL
│   │   └── versions/
│   │       ├── 000000000000_initial.py
│   │       └── 20260924_phase1_finance_verification.py
│   ├── seeds/
│   └── README.md
│
├── docs/                          # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── AUTHENTICATION.md
│   ├── DEPLOYMENT.md
│   ├── SECURITY.md
│   ├── CONTRIBUTING.md
│   ├── TESTING.md
│   └── PROJECT_STRUCTURE.md
│
├── .gitignore
├── .env.example
├── README.md
├── LICENSE
├── alembic.ini
├── docker-compose.yml
└── docs/
```

## Key Design Decisions

1. **Modular Backend**: Each feature area gets its own router file under `api/v1/`
2. **Service Layer**: Business logic lives in `services/`, not in route handlers
3. **Context-Based Frontend State**: React Context for auth, API client, and nav state
4. **CSS Modules**: Per-component CSS files alongside components
5. **Type-Safe Schemas**: Pydantic schemas for all API request/response shapes
6. **JWT Stateless Auth**: No server-side sessions, tokens carry all needed info
