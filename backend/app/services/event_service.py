import uuid
from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func, and_
from app.database import Base, engine
from app.models.event import Event, EventCategory
from app.models.event_image import EventImage
from app.models.ticket import TicketType
from app.models.user import User
from app.models.organizer import OrganizerProfile
from app.models.ticket import Registration, Ticket, TicketScan
from app.models.other import EventReview, Favorite, Notification, AuditLog, Report
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, generate_qr_token
from app.core.config import settings
import qrcode
import io
import os


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_database():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            _seed_users(db)
            _seed_categories(db)
            _seed_events(db)
            db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


def _seed_users(db):
    admin = User(
        email="admin@eventflow.dev",
        username="admin",
        password_hash=hash_password("admin123"),
        first_name="Admin",
        last_name="EventFlow",
        is_active=True,
        is_email_verified=True,
    )
    organizer = User(
        email="organizer@eventflow.dev",
        username="organizer",
        password_hash=hash_password("organizer123"),
        first_name="Kathmandu",
        last_name="Events",
        is_active=True,
        is_email_verified=True,
    )
    user1 = User(
        email="user1@test.com",
        username="user1",
        password_hash=hash_password("user123"),
        first_name="Test",
        last_name="User One",
        is_active=True,
        is_email_verified=True,
    )
    user2 = User(
        email="user2@test.com",
        username="user2",
        password_hash=hash_password("user123"),
        first_name="Test",
        last_name="User Two",
        is_active=True,
        is_email_verified=True,
    )

    db.add_all([admin, organizer, user1, user2])
    db.flush()

    org = OrganizerProfile(
        user_id=organizer.id,
        organization_name="Kathmandu Events Pvt. Ltd.",
        description="Professional event management company based in Kathmandu, Nepal.",
        city="Kathmandu",
        is_verified=True,
    )
    db.add(org)
    db.flush()

    print(f"Seeded users: admin (id={admin.id}), organizer (id={organizer.id}), user1 (id={user1.id}), user2 (id={user2.id})")
    print("WARNING: These are development/test accounts. Do not use in production.")


def _seed_categories(db):
    categories = [
        EventCategory(name="Technology", slug="technology", description="Tech events, conferences, meetups"),
        EventCategory(name="Education", slug="education", description="Educational workshops and seminars"),
        EventCategory(name="Business", slug="business", description="Business networking and conferences"),
        EventCategory(name="Music", slug="music", description="Music concerts and festivals"),
        EventCategory(name="Sports", slug="sports", description="Sports events and tournaments"),
        EventCategory(name="Gaming", slug="gaming", description="Gaming tournaments and events"),
        EventCategory(name="Arts", slug="arts", description="Art exhibitions and cultural events"),
        EventCategory(name="Career", slug="career", description="Career fairs and job events"),
        EventCategory(name="Workshop", slug="workshop", description="Hands-on workshops"),
        EventCategory(name="Conference", slug="conference", description="Professional conferences"),
        EventCategory(name="Community", slug="community", description="Community gatherings"),
        EventCategory(name="Other", slug="other", description="Other events"),
    ]
    db.add_all(categories)
    db.flush()
    print(f"Seeded {len(categories)} categories")


def _seed_events(db):
    from datetime import datetime, timedelta
    categories = db.query(EventCategory).all()
    organizer = db.query(OrganizerProfile).first()
    if not organizer:
        return

    cat_map = {c.name: c for c in categories}
    now = datetime.utcnow()

    events = [
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Technology", categories[0]).id,
            title="Tech Summit Nepal 2026",
            slug="tech-summit-nepal-2026",
            short_description="Nepal's premier technology conference featuring industry leaders",
            full_description="Join us for the biggest technology event in Nepal. Learn from industry leaders, network with professionals, and discover the latest trends in tech.",
            venue="Kathmandu Convention Centre",
            address="Bagmati, Kathmandu",
            city="Kathmandu",
            start_date=now + timedelta(days=30),
            end_date=now + timedelta(days=30),
            max_capacity=200,
            status="PUBLISHED",
            is_featured=True,
            price_min=0.0,
        ),
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Business", categories[2]).id,
            title="Business Networking Mixer",
            slug="business-networking-mixer",
            short_description="Connect with Kathmandu's business community",
            venue="Soaltee Crowne Plaza",
            address="Kathmandu",
            city="Kathmandu",
            start_date=now + timedelta(days=45),
            max_capacity=100,
            status="PUBLISHED",
            price_min=500.0,
        ),
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Music", categories[3]).id,
            title="Nepal Music Festival",
            slug="nepal-music-festival",
            short_description="A celebration of Nepali music and talent",
            venue="Tribhuvan Park",
            address="Kathmandu",
            city="Kathmandu",
            start_date=now + timedelta(days=60),
            end_date=now + timedelta(days=61),
            max_capacity=500,
            status="PUBLISHED",
            is_featured=True,
            price_min=0.0,
        ),
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Workshop", categories[8]).id,
            title="Web Development Workshop",
            slug="web-development-workshop",
            short_description="Hands-on full-stack development workshop",
            venue=" Kathmandu Tech Hub",
            address="KTM",
            city="Kathmandu",
            start_date=now + timedelta(days=14),
            max_capacity=30,
            status="PUBLISHED",
            price_min=250.0,
        ),
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Sports", categories[5]).id,
            title="Kathmandu Marathon 2026",
            slug="kathmandu-marathon-2026",
            short_description="Annual city marathon",
            venue="Kathmandu",
            city="Kathmandu",
            start_date=now + timedelta(days=90),
            max_capacity=300,
            status="PENDING_REVIEW",
            price_min=0.0,
        ),
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Conference", categories[9]).id,
            title="Future of Education Summit",
            slug="future-of-education-summit",
            short_description="Exploring the future of education in Nepal",
            venue="Kathmandu University",
            address="Dhulikhel",
            city="Dhulikhel",
            start_date=now + timedelta(days=75),
            max_capacity=150,
            status="DRAFT",
            price_min=0.0,
        ),
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Career", categories[7]).id,
            title="Career Fair Nepal",
            slug="career-fair-nepal",
            short_description="Job opportunities and career guidance",
            venue="Kathmandu",
            city="Kathmandu",
            start_date=now - timedelta(days=10),
            end_date=now - timedelta(days=10),
            max_capacity=200,
            status="COMPLETED",
            price_min=0.0,
        ),
        Event(
            organizer_id=organizer.id,
            category_id=cat_map.get("Arts", categories[6]).id,
            title="Contemporary Art Exhibition",
            slug="contemporary-art-exhibition",
            short_description="Modern art from Nepali artists",
            venue="Nepal Art Council",
            address="Kathmandu",
            city="Kathmandu",
            start_date=now + timedelta(days=20),
            max_capacity=80,
            status="PUBLISHED",
            price_min=0.0,
        ),
    ]

    db.add_all(events)
    db.flush()

    # Create ticket types for published events
    for event in events[:4]:
        if event.status == "PUBLISHED":
            tts = [
                TicketType(event_id=event.id, name="General", price=event.price_min, currency="NPR", capacity=event.max_capacity, status="ACTIVE"),
                TicketType(event_id=event.id, name="VIP", price=event.price_min * 3 if event.price_min > 0 else 500, currency="NPR", capacity=event.max_capacity // 4, status="ACTIVE"),
            ]
            db.add_all(tts)

    db.flush()
    print(f"Seeded {len(events)} events")
