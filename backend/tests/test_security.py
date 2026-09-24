"""Phase 9 security sweep: authz, payments, capacity, QR reuse, expiry, envelopes."""
import uuid

import pytest
from fastapi.testclient import TestClient

B = "/api/v1"


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _tag(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _user(client, tag=None):
    tag = tag or uuid.uuid4().hex[:8]
    email = f"sec_u_{tag}@test.com"
    tok = client.post(B + "/auth/register",
                      json={"email": email, "username": email, "password": "pass1234"}).json()["data"]["access_token"]
    return tok, {"Authorization": f"Bearer {tok}"}


def _approved_org(client, tag=None):
    tag = tag or uuid.uuid4().hex[:8]
    email = f"sec_o_{tag}@test.com"
    otok = client.post(B + "/auth/organizer/register",
                       json={"email": email, "password": "pass1234",
                             "organization_name": "Sec Org"}).json()["data"]["access_token"]
    atok = client.post(B + "/auth/login",
                       json={"email": "admin@eventflow.dev", "password": "admin123"}).json()["data"]["access_token"]
    apps = client.get(B + "/organizer-applications?status=UNDER_REVIEW",
                      headers={"Authorization": f"Bearer {atok}"}).json()["data"]
    aid = [a for a in apps if a["email"] == email][0]["id"]
    client.post(B + f"/organizer-applications/{aid}/review", json={"action": "APPROVE"},
                headers={"Authorization": f"Bearer {atok}"})
    return otok, {"Authorization": f"Bearer {otok}"}, atok


def _event(client, h, price=0, **kw):
    base = {"title": _tag("SecEv"), "category_id": 4, "start_date": "2027-09-01T18:00:00",
            "max_capacity": 100, "price_min": price}
    base.update(kw)
    ev = client.post(B + "/events", json=base, headers=h).json()["data"]
    client.patch(B + f"/events/{ev['id']}/publish", headers=h)
    tt = client.get(B + f"/events/{ev['id']}/tickets").json()["items"][0]
    return ev, tt


class TestAuthz:
    def test_protected_without_token_401(self, client):
        for path in ["/auth/me", "/tickets/my", "/registrations/me", "/organizer/wallet",
                     "/withdrawals/me", "/users/me", "/notifications/", "/reviews/me"]:
            assert client.get(B + path).status_code == 401, path

    def test_user_cannot_touch_admin(self, client):
        _, uh = _user(client)
        for path in ["/admin/stats", "/admin/events", "/admin/payments", "/admin/wallets",
                     "/admin/settings", "/users/", "/organizer-applications"]:
            assert client.get(B + path, headers=uh).status_code == 403, path

    def test_unapproved_organizer_cannot_publish(self, client):
        email = f"sec_ur_{uuid.uuid4().hex[:8]}@test.com"
        otok = client.post(B + "/auth/organizer/register",
                           json={"email": email, "password": "pass1234",
                                 "organization_name": "UR Org"}).json()["data"]["access_token"]
        h = {"Authorization": f"Bearer {otok}"}
        assert client.post(B + "/events",
                           json={"title": "X", "category_id": 4, "start_date": "2027-09-01T18:00:00"},
                           headers=h).status_code == 403

    def test_cross_organizer_isolation(self, client):
        otok1, h1, _ = _approved_org(client)
        otok2, h2, _ = _approved_org(client)
        ev, _ = _event(client, h1)
        assert client.get(B + f"/organizer/events/{ev['id']}/attendees", headers=h2).status_code == 403
        assert client.put(B + f"/events/{ev['id']}", json={"venue": "Hijack"}, headers=h2).status_code == 403
        assert client.patch(B + f"/events/{ev['id']}/cancel", headers=h2).status_code == 403

    def test_cross_user_ticket_and_order_privacy(self, client):
        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h)
        _, uh1 = _user(client)
        _, uh2 = _user(client)
        client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]}, headers=uh1)
        tid = client.get(B + "/tickets/my", headers=uh1).json()["items"][0]["id"]
        regid = client.get(B + "/registrations/me", headers=uh1).json()["items"][0]["id"]
        assert client.get(B + f"/tickets/{tid}", headers=uh2).status_code == 403
        assert client.get(B + f"/registrations/{regid}", headers=uh2).status_code == 403

    def test_notification_send_admin_only(self, client):
        _, uh = _user(client)
        assert client.post(B + "/notifications/send",
                           json={"user_id": 1, "title": "x", "message": "y"}, headers=uh).status_code == 403


class TestPaymentsSecurity:
    def test_verify_without_initiate_rejected(self, client):
        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h, price=300)
        _, uh = _user(client)
        reg = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                          headers=uh).json()["data"]
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": "bogus"},
                        headers=uh)
        assert r.status_code in (400, 402)

    def test_spoofed_success_rejected(self, client):
        import base64
        import json as pyjson

        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h, price=300)
        _, uh = _user(client)
        reg = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                          headers=uh).json()["data"]
        init = client.post(B + "/payments/initiate",
                           json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                           headers=uh).json()["data"]
        fake = base64.b64encode(pyjson.dumps(
            {"status": "COMPLETE", "total_amount": "300.00", "transaction_uuid": init["transaction_id"]}).encode()).decode()
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": fake},
                        headers=uh)
        assert r.status_code in (400, 402)
        # order still payable, no ticket minted
        assert client.get(B + "/tickets/my", headers=uh).json()["items"] == []

    def test_other_user_cannot_pay_my_order(self, client):
        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h, price=300)
        _, uh1 = _user(client)
        _, uh2 = _user(client)
        reg = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                          headers=uh1).json()["data"]
        assert client.post(B + "/payments/initiate",
                           json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                           headers=uh2).status_code == 403


class TestCapacityAndExpiry:
    def test_event_capacity_enforced(self, client):
        from app.database import SessionLocal
        from app.models.ticket import TicketType

        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h)
        db = SessionLocal()
        row = db.query(TicketType).filter(TicketType.id == tt["id"]).first()
        row.capacity = 1
        db.commit()
        db.close()
        _, uh1 = _user(client)
        _, uh2 = _user(client)
        assert client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                           headers=uh1).status_code == 200
        assert client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                           headers=uh2).status_code == 400

    def test_ended_hidden_but_in_history(self, client):
        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h, title=_tag("Oldie"),
                        start_date="2020-01-01T10:00:00", end_date="2020-01-01T12:00:00")
        public = client.get(B + "/events?q=Oldie").json()["items"]
        assert all(e["id"] != ev["id"] for e in public)
        detail = client.get(B + f"/events/{ev['id']}").json()["data"]
        assert detail["lifecycle"] == "ENDED"
        # owner history keeps it
        mine = client.get(B + "/organizer/events?lifecycle=ENDED", headers=h).json()["items"]
        assert any(e["id"] == ev["id"] for e in mine)

    def test_cancelled_blocks_purchase(self, client):
        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h)
        client.patch(B + f"/events/{ev['id']}/cancel", headers=h)
        _, uh = _user(client)
        assert client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                           headers=uh).status_code == 400
        assert all(e["id"] != ev["id"] for e in client.get(B + "/events").json()["items"])


class TestQrReuse:
    def test_reuse_blocked_on_both_paths(self, client):
        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h)
        _, uh = _user(client)
        qr = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                         headers=uh).json()["data"]["qr_token"]
        assert client.post(B + "/organizer/scan", json={"qr_token": qr, "event_id": ev["id"]},
                           headers=h).status_code == 200
        assert client.post(B + "/organizer/scan", json={"qr_token": qr, "event_id": ev["id"]},
                           headers=h).status_code == 400
        assert client.post(B + "/checkins/verify", json={"qr_token": qr},
                           headers=h).status_code == 400


class TestEnvelopes:
    def test_consistent_envelope_and_json(self, client):
        otok, h, _ = _approved_org(client)
        ev, tt = _event(client, h)
        for path, headers in [(B + "/events", None), (B + "/categories", None),
                              (B + f"/events/{ev['id']}", None),
                              (B + "/organizer/wallet", h)]:
            r = client.get(path, headers=headers) if headers else client.get(path)
            assert r.status_code == 200, path
            assert r.headers["content-type"].startswith("application/json"), path
            assert r.json().get("success") is True, path
