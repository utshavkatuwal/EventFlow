import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


class TestRegistration:
    def test_create_registration(self, client):
        # Register and login first
        email = f"reg_{id}_test@test.com"
        client.post("/api/v1/auth/register", json={
            "email": email, "username": email, "password": "Test123456",
        })
        login = client.post("/api/v1/auth/login", json={
            "email": email, "password": "Test123456",
        })
        token = login.json()["access_token"]
        
        r = client.post("/api/v1/registrations", json={
            "event_id": 1, "ticket_type_id": 1,
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code in [200, 400]


class TestTicketRetrieval:
    def test_get_my_tickets_requires_auth(self, client):
        r = client.get("/api/v1/tickets/my")
        assert r.status_code == 401


class TestSearch:
    def test_search_events(self, client):
        r = client.get("/api/v1/search/?q=technology")
        assert r.status_code == 200


class TestNotifications:
    def test_list_notifications_requires_auth(self, client):
        r = client.get("/api/v1/notifications/")
        assert r.status_code == 401
