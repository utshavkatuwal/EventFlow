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
│   │   │   └── RoleGuard.jsx
│   │   ├── pages/                 # Page components
│   │   │   ├── HomePage.jsx
│   │   │   ├── EventsPage.jsx
│   │   │   ├── EventDetailPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── UserDashboardPage.jsx
│   │   │   ├── OrganizerDashboardPage.jsx
│   │   │   ├── AdminDashboardPage.jsx
│   │   │   ├── TicketPage.jsx
│   │   │   ├── CheckInPage.jsx
│   │   │   ├── ProfilePage.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── layouts/               # Page layouts
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── services/              # API service layer
│   │   │   └── api.js
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
│   ├── tests/                     # Frontend tests
│   ├── package.json
│   └── vite.config.js
│
├── backend/                       # FastAPI backend
│   ├── app/
│   │   ├── main.py               # Application entry point
│   │   ├── core/
│   │   │   ├── config.py         # Settings
│   │   │   └── security.py       # Auth utilities
│   │   ├── config/               # Configuration modules
│   │   ├── database/
│   │   │   └── __init__.py       # DB connection, session, models base
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   ├── organizer.py
│   │   │   ├── event_image.py
│   │   │   ├── ticket.py
│   │   │   └── other.py
│   │   ├── schemas/              # Pydantic validation
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   └── v1/               # API version 1
│   │   │       ├── router.py     # Main router
│   │   │       ├── events_router.py
│   │   │       ├── categories_router.py
│   │   │       ├── user_router.py
│   │   │       ├── tickets_router.py
│   │   │       ├── reviews_router.py
│   │   │       ├── notifications_router.py
│   │   │       ├── search_router.py
│   │   │       ├── admin_router.py
│   │   │       ├── organizers_router.py
│   │   │       └── users_router.py
│   │   ├── services/             # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── event_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── public_service.py
│   │   │   ├── file_service.py
│   │   │   └── file_utils.py
│   │   ├── repositories/         # Data access layer
│   │   ├── auth/
│   │   │   └── dependencies.py
│   │   └── utils/
│   ├── scripts/
│   │   └── seed.py               # Database seeding
│   ├── docs/
│   ├── requirements.txt
│   └── package.json
│
├── database/                      # Database schema & seeds
│   ├── migrations/               # Alembic migrations
│   │   ├── env.py
│   │   └── versions/
│   │       └── 000000000000_initial.py
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
