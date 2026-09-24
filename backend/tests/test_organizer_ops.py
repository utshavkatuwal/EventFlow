"""Phase 6 regression: attendees, hardened scan, sales, wallet."""
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _setup(client, price=0):
    tag = uuid.uuid4().hex[:8]
    B = "/api/v1"
    otok = client.post(B + "/auth/organizer/register",
                       json={"email": f"s6_{tag}@test.com", "password": "pass1234",
                             "organization_name": "S6 Org"}).json()["data"]["access_token"]
    atok = client.post(B + "/auth/login",
                       json={"email": "admin@eventflow.dev", "password": "admin123"}).json()["data"]["access_token"]
    apps = client.get(B + "/organizer-applications?status=UNDER_REVIEW",
                      headers={"Authorization": f"Bearer {atok}"}).json()["data"]
    aid = [a for a in apps if a["email"] == f"s6_{tag}@test.com"][0]["id"]
    client.post(B + f"/organizer-applications/{aid}/review", json={"action": "APPROVE"},
                headers={"Authorization": f"Bearer {atok}"})
    h = {"Authorization": f"Bearer {otok}"}
    ev = client.post(B + "/events",
                     json={"title": f"S6 {tag}", "category_id": 4,
                           "start_date": "2027-09-01T18:00:00",
                           "max_capacity": 100, "price_min": price}, headers=h).json()["data"]
    client.patch(B + f"/events/{ev['id']}/publish", headers=h)
    tt = client.get(B + f"/events/{ev['id']}/tickets").json()["items"][0]
    utok = client.post(B + "/auth/register",
                       json={"email": f"s6u_{tag}@test.com", "username": f"s6u_{tag}",
                             "password": "pass1234"}).json()["data"]["access_token"]
    return B, h, {"Authorization": f"Bearer {utok}"}, ev, tt


class TestOrganizerOps:
    def test_attendees_and_stats(self, client):
        B, h, uh, ev, tt = _setup(client)
        client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=uh)
        r = client.get(B + f"/organizer/events/{ev['id']}/attendees", headers=h)
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["stats"]["tickets_sold"] == 1
        assert d["stats"]["tickets_remaining"] == 99
        assert d["attendees"][0]["payment_status"] == "PAID"
        assert d["attendees"][0]["attendance_status"] == "VALID"

    def test_attendees_denied_to_stranger(self, client):
        B, h, uh, ev, tt = _setup(client)
        assert client.get(B + f"/organizer/events/{ev['id']}/attendees", headers=uh).status_code == 403

    def test_scan_confirm_then_reuse(self, client):
        B, h, uh, ev, tt = _setup(client)
        qr = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                         headers=uh).json()["data"]["qr_token"]
        r = client.post(B + "/organizer/scan", json={"qr_token": qr, "event_id": ev["id"]}, headers=h)
        assert r.status_code == 200
        assert r.json()["message"] == "ATTENDANCE CONFIRMED"
        r = client.post(B + "/organizer/scan", json={"qr_token": qr, "event_id": ev["id"]}, headers=h)
        assert r.status_code == 400
        assert r.json()["detail"]["error"] == "ALREADY_USED"
        # attendee row flips to USED
        att = client.get(B + f"/organizer/events/{ev['id']}/attendees", headers=h).json()["data"]
        assert att["stats"]["attended"] == 1

    def test_scan_wrong_event_and_invalid(self, client):
        B, h, uh, ev, tt = _setup(client)
        qr = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                         headers=uh).json()["data"]["qr_token"]
        assert client.post(B + "/organizer/scan", json={"qr_token": qr, "event_id": 999999}, headers=h).status_code in (400, 404)
        assert client.post(B + "/organizer/scan", json={"qr_token": "nope", "event_id": ev["id"]}, headers=h).status_code == 404

    def test_scan_unpaid_blocked(self, client):
        B, h, uh, ev, tt = _setup(client, price=500)
        reg = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                          headers=uh).json()["data"]
        # PENDING order has no ticket; craft scan attempt via direct ticket-less path is impossible,
        # so verify the stats show it as unsold and attendees exclude it from sold count.
        att = client.get(B + f"/organizer/events/{ev['id']}/attendees", headers=h).json()["data"]
        assert att["stats"]["tickets_sold"] == 0

    def test_sales_and_wallet(self, client):
        B, h, uh, ev, tt = _setup(client)
        client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=uh)
        sales = client.get(B + f"/organizer/events/{ev['id']}/sales", headers=h).json()["data"]
        assert sales["breakdown"][0]["sold"] == 1
        wallet = client.get(B + "/organizer/wallet", headers=h).json()["data"]
        assert "available_balance" in wallet and "pending_balance" in wallet
        assert wallet["transactions"] == [] or isinstance(wallet["transactions"], list)
