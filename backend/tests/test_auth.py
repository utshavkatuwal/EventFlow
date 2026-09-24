import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestAuth:
    def test_register_returns_user_id(self, client):
        import uuid
        uid = uuid.uuid4().hex[:8]
        r = client.post("/api/v1/auth/register", json={
            "email": f"test_{uid}_a@test.com",
            "username": f"test_a_{uid}",
            "password": "Test123456",
        })
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_login_returns_tokens(self, client):
        import uuid
        uid = uuid.uuid4().hex[:8]
        email = f"login_{uid}_b@test.com"
        client.post("/api/v1/auth/register", json={
            "email": email, "username": email, "password": "Test123456",
        })
        r = client.post("/api/v1/auth/login", json={
            "email": email, "password": "Test123456",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_fails_with_wrong_password(self, client):
        r = client.post("/api/v1/auth/login", json={
            "email": "wrong@test.com", "password": "wrong",
        })
        assert r.status_code == 401

    def test_protected_route_requires_auth(self, client):
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 401


class TestEvents:
    def test_get_events(self, client):
        r = client.get("/api/v1/events/")
        assert r.status_code == 200
        assert "items" in r.json()

    def test_get_event_stats(self, client):
        r = client.get("/api/v1/events/stats")
        assert r.status_code == 200


class TestCategories:
    def test_list_categories(self, client):
        r = client.get("/api/v1/categories/")
        assert r.status_code == 200
