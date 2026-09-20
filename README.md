# EventFlow

A professional event discovery, registration, ticketing, and event management web application focused on events in Nepal.

## Project Overview

EventFlow is a modern event platform that enables users to discover, search, filter, and register for events. Organizers can create and manage events, configure ticket types, check in attendees via QR codes, and view analytics. Administrators can moderate content, manage users and organizers, and monitor platform activity.

## Features

### For Users
- Browse and discover events
- Search events by title, description, category, organizer, location
- Filter and sort events
- Register for events with ticket selection
- View digital tickets with QR codes
- Save favorite events
- Write reviews for attended events
- Manage profile and notifications

### For Organizers
- Create, edit, and publish events
- Configure ticket types and capacity
- Manage registrations and attendees
- Check in attendees via QR code scanning
- View event analytics
- Manage organizer profile

### For Administrators
- Approve or reject events
- Manage users and organizers
- Manage categories
- Review reports
- View audit logs
- Platform analytics

## Tech Stack

- **Frontend**: React 18, Vite, React Router, CSS Modules
- **Backend**: FastAPI (Python 3.11+)
- **Database**: MySQL 8.0
- **Authentication**: JWT tokens (access + refresh)
- **QR Codes**: qrcode library with Pillow
- **Icons**: Custom SVG icons

## Architecture

```
frontend/     - React SPA (port 5173)
backend/      - FastAPI REST API (port 8000)
database/     - SQLAlchemy models, migrations, seeds
docs/         - Project documentation
```

The backend exposes a versioned REST API at `/api/v1/` designed to be consumed by any client (web, Flutter mobile app in future phases).

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Docker (optional)

### Database Setup

```bash
# Using Docker
docker-compose up -d mysql

# Or manually
createdb eventflow
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env      # Edit with your credentials

# Run migrations
alembic upgrade head

# Seed development data
python scripts/seed.py

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **API Docs**: [docs/API.md](docs/API.md)

## Project Structure

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed directory layout.

## Testing

Backend: `pytest backend/tests/`
Frontend: `cd frontend && npm test`

See [docs/TESTING.md](docs/TESTING.md) for details.

## Security

See [docs/SECURITY.md](docs/SECURITY.md) for security measures and best practices.

## Contribution

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## Roadmap

- [x] Core platform architecture
- [x] User authentication and authorization
- [x] Event discovery and search
- [ ] Payment gateway integration (paid tickets)
- [ ] Push notifications (Flutter)
- [ ] Flutter mobile application
- [ ] Advanced analytics dashboard
- [ ] Email/SMS notifications

## Future Flutter Application Architecture

The REST API is designed to be consumed by a Flutter application in a future phase. All endpoints follow REST conventions with JSON responses. The API is platform-agnostic.

Key endpoints for Flutter:
- `POST /api/v1/auth/login`
- `GET /api/v1/events`
- `GET /api/v1/events/{id}`
- `POST /api/v1/events/{id}/register`
- `GET /api/v1/users/me/tickets`
- `POST /api/v1/checkins/verify`

## License

MIT License — see [LICENSE](LICENSE).
