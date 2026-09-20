"""Database seed script for development"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.core.config import settings
from app.services.event_service import seed_database


def main():
    print("Starting database seed...")
    print(f"Database URL: {settings.DATABASE_URL}")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Tables ensured.")

    # Seed data
    seed_database()

    print("Seed complete!")
    print("\nDevelopment accounts:")
    print("  Admin: admin@eventflow.dev / admin123")
    print("  Organizer: organizer@eventflow.dev / organizer123")
    print("  Test User: user1@test.com / user123")
    print("  Test User: user2@test.com / user123")
    print("\nWARNING: These are development/test accounts. Do not use in production.")


if __name__ == "__main__":
    main()
