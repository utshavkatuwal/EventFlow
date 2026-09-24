import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


class TestEventCreation:
    def test_create_event_requires_auth(self, client):
        response = client.post("/api/v1/events", json={"title": "Test Event"})
        assert response.status_code == 401

    def test_create_event_with_auth(self, client):
        # Register and login
        import uuid
        uid = uuid.uuid4().hex[:8]
        email = f"organizer_test_{uid}@test.com"
        client.post("/api/v1/auth/register", json={
            "email": email, "username": email, "password": "Test123456",
        })
        login = client.post("/api/v1/auth/login", json={
            "email": email, "password": "Test123456",
        })
        token = login.json()["access_token"]
        
        # Create organizer profile first (would need organizer role)
        response = client.post("/api/v1/events", json={
            "title": "Test Event",
            "category_id": 1,
            "start_date": "2026-12-01",
            "max_capacity": 100,
        }, headers={"Authorization": f"Bearer {token}"})
        # Should fail without organizer profile
        assert response.status_code == 403


class TestOrganizerProfile:
    def test_get_profile_requires_auth(self, client):
        response = client.get("/api/v1/organizer/profile")
        assert response.status_code == 401