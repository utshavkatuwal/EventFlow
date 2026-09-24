"""Database connection and session management for EventFlow"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_phase1_schema() -> None:
    """Create new tables + backfill new columns on existing dev DBs.

    - New tables are created via Base.metadata.create_all.
    - New columns on users / organizer_profiles are added with ALTER TABLE
      when missing (SQLite + MySQL compatible path dùng PRAGMA / information_schema).
    Safe to run on every startup (idempotent).
    """
    try:
        # Import models so metadata is complete
        import app.database.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    try:
        from sqlalchemy import inspect, text

        insp = inspect(engine)
        # users.account_type
        if "users" in insp.get_table_names():
            cols = {c["name"] for c in insp.get_columns("users")}
            if "account_type" not in cols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN account_type VARCHAR(20) DEFAULT 'USER'"))
            # backfill NULLs
            with engine.begin() as conn:
                conn.execute(text("UPDATE users SET account_type='USER' WHERE account_type IS NULL"))
        if "events" in insp.get_table_names():
            cols = {c["name"] for c in insp.get_columns("events")}
            if "video_url" not in cols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE events ADD COLUMN video_url VARCHAR(500)"))
        if "organizer_profiles" in insp.get_table_names():
            cols = {c["name"] for c in insp.get_columns("organizer_profiles")}
            with engine.begin() as conn:
                if "verification_status" not in cols:
                    conn.execute(
                        text("ALTER TABLE organizer_profiles ADD COLUMN verification_status VARCHAR(20) DEFAULT 'UNDER_REVIEW'")
                    )
                if "verification_info" not in cols:
                    conn.execute(text("ALTER TABLE organizer_profiles ADD COLUMN verification_info TEXT"))
                if "rejection_reason" not in cols:
                    conn.execute(text("ALTER TABLE organizer_profiles ADD COLUMN rejection_reason TEXT"))
            # legacy is_verified=True  => APPROVED
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "UPDATE organizer_profiles SET verification_status='APPROVED' "
                        "WHERE verification_status IS NULL OR (verification_status='UNDER_REVIEW' AND is_verified=1)"
                    )
                )
        # seed default platform settings
        from app.models.finance import DEFAULT_SETTINGS, PlatformSetting

        db = SessionLocal()
        try:
            for key, (value, desc) in DEFAULT_SETTINGS.items():
                if not db.query(PlatformSetting).filter(PlatformSetting.key == key).first():
                    db.add(PlatformSetting(key=key, value=value, description=desc))
            # ensure base roles exist
            from app.models.user import Role, User, UserRole

            role_map = {}
            for name, rdesc in [
                ("admin", "Platform administrator"),
                ("organizer", "Approved event organizer"),
                ("user", "Standard user"),
            ]:
                r = db.query(Role).filter(Role.name == name).first()
                if not r:
                    r = Role(name=name, description=rdesc)
                    db.add(r)
                    db.flush()
                role_map[name] = r
            # backfill dev accounts (idempotent)
            from app.core.security import hash_password as _hash

            for email, atype, rname, pwd in [
                ("admin@eventflow.dev", "ADMIN", "admin", "admin123"),
                ("organizer@eventflow.dev", "ORGANIZER", "organizer", "organizer123"),
                ("user1@test.com", "USER", "user", "user123"),
                ("user2@test.com", "USER", "user", "user123"),
            ]:
                u = db.query(User).filter(User.email == email).first()
                if u:
                    # dev seed accounts: enforce documented account types
                    u.account_type = atype
                    # repair stale bcrypt hashes from older seed runs (dev only)
                    try:
                        from app.core.security import verify_password as _verify

                        if not _verify(pwd, u.password_hash):
                            u.password_hash = _hash(pwd)
                    except Exception:
                        u.password_hash = _hash(pwd)
                    if not db.query(UserRole).filter(
                        UserRole.user_id == u.id, UserRole.role_id == role_map[rname].id
                    ).first():
                        db.add(UserRole(user_id=u.id, role_id=role_map[rname].id))
            # every PUBLISHED/APPROVED event needs at least one bookable ticket type
            try:
                from app.models.event import Event as _Event
                from app.models.ticket import TicketType as _TT
                for ev in db.query(_Event).filter(_Event.status.in_(["PUBLISHED", "APPROVED"])).all():
                    if not db.query(_TT).filter(_TT.event_id == ev.id).first():
                        db.add(_TT(event_id=ev.id, name="General", price=float(ev.price_min or 0.0),
                                   currency="NPR", capacity=int(ev.max_capacity or 100), status="ACTIVE"))
            except Exception:
                pass
            db.commit()
        finally:
            db.close()
    except Exception:
        pass
