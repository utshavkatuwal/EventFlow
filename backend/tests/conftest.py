"""Pytest bootstrap: isolated test DB + no rate limits.

Tests run against a fresh SQLite file (never the dev database), seeded with
the same 12 categories (same ids/order as dev seed) and the documented admin
account. Deterministic on every run.
"""
import os

_TEST_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_eventflow.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)

os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ["EVENTFLOW_TESTING"] = "1"
# Unit tests simulate the provider response offline; the live status lookup
# is covered by integration config (default true in production).
os.environ["ESEWA_STATUS_CHECK"] = "false"

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _seed_test_db():
    from app.core.security import hash_password
    from app.database import SessionLocal, ensure_phase1_schema
    from app.models.event import EventCategory
    from app.models.user import Role, User, UserRole

    ensure_phase1_schema()
    db = SessionLocal()
    try:
        names = ["Technology", "Education", "Business", "Music", "Sports", "Gaming",
                 "Arts", "Career", "Workshop", "Conference", "Community", "Other"]
        for n in names:
            if not db.query(EventCategory).filter(EventCategory.name == n).first():
                db.add(EventCategory(name=n, slug=n.lower(),
                                     description=f"{n} events"))
        db.flush()
        admin = db.query(User).filter(User.email == "admin@eventflow.dev").first()
        if not admin:
            admin = User(email="admin@eventflow.dev", username="admin",
                         password_hash=hash_password("admin123"),
                         first_name="Admin", last_name="EventFlow",
                         is_active=True, is_email_verified=True, account_type="ADMIN")
            db.add(admin)
            db.flush()
        role = db.query(Role).filter(Role.name == "admin").first()
        if role and not db.query(UserRole).filter(
                UserRole.user_id == admin.id, UserRole.role_id == role.id).first():
            db.add(UserRole(user_id=admin.id, role_id=role.id))
        db.commit()
    finally:
        db.close()
    yield
