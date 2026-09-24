"""Phase 8 regression: admin stats, payments, wallets, settings."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_h(client):
    tok = client.post("/api/v1/auth/login",
                      json={"email": "admin@eventflow.dev", "password": "admin123"}).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {tok}"}


class TestAdmin:
    def test_stats_shape(self, client, admin_h):
        d = client.get("/api/v1/admin/stats", headers=admin_h).json()["data"]
        for key in ["total_users", "total_organizers", "pending_organizers", "approved_organizers",
                    "total_events", "active_events", "ended_events", "tickets_sold",
                    "transaction_volume", "wallet_available_total", "wallet_pending_total",
                    "pending_withdrawals", "completed_withdrawals"]:
            assert key in d, key

    def test_admin_denied_to_user(self, client):
        import uuid

        uid = uuid.uuid4().hex[:8]
        utok = client.post("/api/v1/auth/register",
                           json={"email": f"adm8x_{uid}@test.com", "username": f"adm8x_{uid}",
                                 "password": "pass1234"}).json()["data"]["access_token"]
        assert client.get("/api/v1/admin/stats",
                          headers={"Authorization": f"Bearer {utok}"}).status_code == 403
        assert client.get("/api/v1/admin/settings",
                          headers={"Authorization": f"Bearer {utok}"}).status_code == 403

    def test_settings_editable_and_guarded(self, client, admin_h):
        assert client.patch("/api/v1/admin/settings", json={"key": "nope", "value": 1},
                            headers=admin_h).status_code == 400
        assert client.patch("/api/v1/admin/settings",
                            json={"key": "withdrawal_service_fee", "value": -5},
                            headers=admin_h).status_code == 400
        assert client.patch("/api/v1/admin/settings",
                            json={"key": "settlement_hold_days", "value": 3},
                            headers=admin_h).status_code == 200
        assert client.get("/api/v1/admin/settings", headers=admin_h).json()["data"]["settlement_hold_days"] == "3"
        client.patch("/api/v1/admin/settings", json={"key": "settlement_hold_days", "value": 2},
                     headers=admin_h)

    def test_payments_and_wallets_visible(self, client, admin_h):
        assert client.get("/api/v1/admin/payments", headers=admin_h).status_code == 200
        assert "volume" in client.get("/api/v1/admin/payments", headers=admin_h).json()
        assert client.get("/api/v1/admin/wallets", headers=admin_h).status_code == 200
        assert client.get("/api/v1/admin/events", headers=admin_h).status_code == 200
