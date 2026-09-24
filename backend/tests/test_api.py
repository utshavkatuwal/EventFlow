import pytest
import json
from fastapi.testclient import TestClient


# These tests require the app to be importable
# Run from backend directory: pytest tests/ -v

def test_health_endpoint():
    """Test that health endpoint returns 200"""
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test that root endpoint returns API info"""
    from app.main import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "EventFlow" in response.json().get("message", "")


def test_categories_list():
    """Test categories API endpoint"""
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_events_list():
    """Test events API endpoint returns events"""
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/events/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_events_stats():
    """Test events stats endpoint"""
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/events/stats")
    assert response.status_code == 200


def test_register_user():
    """Test user registration"""
    import uuid
    from app.main import app
    client = TestClient(app)
    uid = uuid.uuid4().hex[:8]
    payload = {
        "email": f"test_register_{uid}@test.com",
        "username": f"test_reg_{uid}",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "user_id" in data.get("data", {})


def test_login_success():
    """Test successful login"""
    import uuid
    from app.main import app
    client = TestClient(app)
    uid = uuid.uuid4().hex[:8]
    # First register
    reg_payload = {
        "email": f"login_test_{uid}@test.com",
        "username": f"login_test_{uid}",
        "password": "testpass123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)
    
    # Then login
    login_payload = {"email": f"login_test_{uid}@test.com", "password": "testpass123"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials():
    """Test login with wrong password"""
    from app.main import app
    client = TestClient(app)
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_duplicate_registration():
    """Test that duplicate email registration fails"""
    import uuid
    from app.main import app
    client = TestClient(app)
    uid = uuid.uuid4().hex[:8]
    payload = {
        "email": f"dup_test_{uid}@test.com",
        "username": f"dup_test_{uid}",
        "password": "testpass123",
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


def test_requires_auth_for_protected_routes():
    """Test that protected routes return 401 without token"""
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
