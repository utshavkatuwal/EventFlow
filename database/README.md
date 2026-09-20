# EventFlow Database README

## Setup

The database runs in MySQL 8.0. See `docs/DEPLOYMENT.md` for setup instructions.

## Migrations

Migrations use Alembic:

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Seeding

Development seed data:

```bash
python scripts/seed.py
```

This creates:
- Admin account (admin@eventflow.dev / admin123)
- Organizer account (organizer@eventflow.dev / organizer123)
- Test users (user1@test.com / user123, user2@test.com / user123)
- 12 event categories
- 8 sample events in various statuses

## Status

- Initial migration: Complete
- Seeding: Complete
