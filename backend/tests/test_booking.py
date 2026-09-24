"""Phase 4 regression: booking, capacity, tickets, QR."""
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _approved_organizer(client, tag):
    email = f"bk_org_{tag}@test.com"
    otok = client.post(
        "/api/v1/auth/organizer/register",
        json={"email": email, "password": "pass1234", "organization_name": "BK Org"},
    ).json()["data"]["access_token"]
    atok = client.post(
        "/api/v1/auth/login", json={"email": "admin@eventflow.dev", "password": "admin123"}
    ).json()["data"]["access_token"]
    apps = client.get(
        "/api/v1/organizer-applications?status=UNDER_REVIEW",
        headers={"Authorization": f"Bearer {atok}"},
    ).json()["data"]
    aid = [a for a in apps if a["email"] == email][0]["id"]
    client.post(
        f"/api/v1/organizer-applications/{aid}/review",
        json={"action": "APPROVE"},
        headers={"Authorization": f"Bearer {atok}"},
    )
    return otok


def _user(client, tag):
    email = f"bk_u_{tag}@test.com"
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": email, "password": "pass1234"},
    ).json()["data"]["access_token"]


def _event(client, otok, **kw):
    base = {"title": "BK", "category_id": 4, "start_date": "2027-08-01T18:00:00",
            "max_capacity": 100, "price_min": 0}
    base.update(kw)
    ev = client.post("/api/v1/events", json=base,
                     headers={"Authorization": f"Bearer {otok}"}).json()["data"]
    client.patch(f"/api/v1/events/{ev['id']}/publish",
                 headers={"Authorization": f"Bearer {otok}"})
    tt = client.get(f"/api/v1/events/{ev['id']}/tickets").json()["items"][0]
    return ev, tt


class TestBooking:
    def test_free_booking_issues_ticket_with_qr(self, client):
        tag = uuid.uuid4().hex[:8]
        otok = _approved_organizer(client, tag)
        ev, tt = _event(client, otok, title=f"Free {tag}")
        utok = _user(client, tag)
        r = client.post("/api/v1/registrations",
                        json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                        headers={"Authorization": f"Bearer {utok}"})
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["ticket_code"].startswith("EV-")
        assert d["qr_token"]
        assert d["qr_code_url"].endswith(".png")

    def test_duplicate_booking_rejected(self, client):
        tag = uuid.uuid4().hex[:8]
        otok = _approved_organizer(client, tag)
        ev, tt = _event(client, otok, title=f"Dup {tag}")
        utok = _user(client, tag)
        h = {"Authorization": f"Bearer {utok}"}
        assert client.post("/api/v1/registrations",
                           json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=h).status_code == 200
        assert client.post("/api/v1/registrations",
                           json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=h).status_code == 409

    def test_paid_booking_stays_pending(self, client):
        tag = uuid.uuid4().hex[:8]
        otok = _approved_organizer(client, tag)
        ev, tt = _event(client, otok, title=f"Paid {tag}", price_min=500)
        utok = _user(client, tag)
        r = client.post("/api/v1/registrations",
                        json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                        headers={"Authorization": f"Bearer {utok}"})
        assert r.status_code == 200
        assert r.json()["data"]["payment_required"] is True
        regs = client.get("/api/v1/registrations/me",
                          headers={"Authorization": f"Bearer {utok}"}).json()["items"]
        assert regs[0]["status"] == "PENDING"
        # no ticket yet
        assert client.get("/api/v1/tickets/my",
                          headers={"Authorization": f"Bearer {utok}"}).json()["items"] == []

    def test_sold_out_and_ended_blocked(self, client):
        from app.database import SessionLocal
        from app.models.ticket import TicketType

        tag = uuid.uuid4().hex[:8]
        otok = _approved_organizer(client, tag)
        ev, tt = _event(client, otok, title=f"Tiny {tag}")
        db = SessionLocal()
        row = db.query(TicketType).filter(TicketType.id == tt["id"]).first()
        row.capacity = 1
        db.commit()
        db.close()
        u1 = _user(client, tag + "a")
        u2 = _user(client, tag + "b")
        h1, h2 = {"Authorization": f"Bearer {u1}"}, {"Authorization": f"Bearer {u2}"}
        assert client.post("/api/v1/registrations",
                           json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=h1).status_code == 200
        assert client.post("/api/v1/registrations",
                           json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=h2).status_code == 400
        ev_old, tt_old = _event(client, otok, title=f"Old {tag}",
                                start_date="2020-01-01T10:00:00", end_date="2020-01-01T12:00:00")
        assert client.post("/api/v1/registrations",
                           json={"event_id": ev_old["id"], "ticket_type_id": tt_old["id"]},
                           headers=h1).status_code == 400

    def test_cancel_then_rebook(self, client):
        tag = uuid.uuid4().hex[:8]
        otok = _approved_organizer(client, tag)
        ev, tt = _event(client, otok, title=f"Re {tag}", price_min=100)
        utok = _user(client, tag)
        h = {"Authorization": f"Bearer {utok}"}
        reg = client.post("/api/v1/registrations",
                          json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=h).json()["data"]
        assert client.post(f"/api/v1/registrations/{reg['registration_id']}/cancel", headers=h).status_code == 200
        assert client.post("/api/v1/registrations",
                           json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=h).status_code == 200

    def test_ticket_visible_only_to_owner(self, client):
        tag = uuid.uuid4().hex[:8]
        otok = _approved_organizer(client, tag)
        ev, tt = _event(client, otok, title=f"Priv {tag}")
        u1 = _user(client, tag + "a")
        u2 = _user(client, tag + "b")
        client.post("/api/v1/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                    headers={"Authorization": f"Bearer {u1}"})
        tid = client.get("/api/v1/tickets/my",
                         headers={"Authorization": f"Bearer {u1}"}).json()["items"][0]["id"]
        assert client.get(f"/api/v1/tickets/{tid}",
                          headers={"Authorization": f"Bearer {u1}"}).status_code == 200
        assert client.get(f"/api/v1/tickets/{tid}",
                          headers={"Authorization": f"Bearer {u2}"}).status_code == 403
