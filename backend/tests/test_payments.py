"""Phase 5 regression: eSewa verify, idempotency, ledger, Khalti honesty."""
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _setup_paid(client, price=500):
    tag = uuid.uuid4().hex[:8]
    B = "/api/v1"
    otok = client.post(B + "/auth/organizer/register",
                       json={"email": f"p5_{tag}@test.com", "password": "pass1234",
                             "organization_name": "P5 Org"}).json()["data"]["access_token"]
    atok = client.post(B + "/auth/login",
                       json={"email": "admin@eventflow.dev", "password": "admin123"}).json()["data"]["access_token"]
    apps = client.get(B + "/organizer-applications?status=UNDER_REVIEW",
                      headers={"Authorization": f"Bearer {atok}"}).json()["data"]
    aid = [a for a in apps if a["email"] == f"p5_{tag}@test.com"][0]["id"]
    client.post(B + f"/organizer-applications/{aid}/review", json={"action": "APPROVE"},
                headers={"Authorization": f"Bearer {atok}"})
    h = {"Authorization": f"Bearer {otok}"}
    ev = client.post(B + "/events",
                     json={"title": f"P5 {tag}", "category_id": 4,
                           "start_date": "2027-09-01T18:00:00",
                           "max_capacity": 50, "price_min": price}, headers=h).json()["data"]
    client.patch(B + f"/events/{ev['id']}/publish", headers=h)
    tt = client.get(B + f"/events/{ev['id']}/tickets").json()["items"][0]
    utok = client.post(B + "/auth/register",
                       json={"email": f"p5u_{tag}@test.com", "username": f"p5u_{tag}",
                             "password": "pass1234"}).json()["data"]["access_token"]
    uh = {"Authorization": f"Bearer {utok}"}
    reg = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                      headers=uh).json()["data"]
    return B, h, uh, ev, reg


class TestEsewa:
    def test_initiate_returns_signed_fields(self, client):
        B, h, uh, ev, reg = _setup_paid(client)
        r = client.post(B + "/payments/initiate",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA"}, headers=uh)
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["action_url"].startswith("https://")
        assert "signature" in d["fields"]
        assert d["fields"]["transaction_uuid"] == d["transaction_id"]

    def test_verify_issues_ticket_and_ledger(self, client):
        from app.services.payments.esewa import build_test_response

        B, h, uh, ev, reg = _setup_paid(client)
        init = client.post(B + "/payments/initiate",
                           json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                           headers=uh).json()["data"]
        good = build_test_response(transaction_id=init["transaction_id"], amount=500)
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": good},
                        headers=uh)
        assert r.status_code == 200
        assert r.json()["data"]["ticket_code"].startswith("EV-")
        wallet = client.get(B + "/payments/wallet", headers=h).json()["data"]
        assert wallet["pending_balance"] == 480.0
        kinds = {t["type"] for t in wallet["transactions"]}
        assert {"TICKET_SALE", "PLATFORM_FEE"} <= kinds

    def test_double_verify_no_duplicate(self, client):
        from app.services.payments.esewa import build_test_response

        B, h, uh, ev, reg = _setup_paid(client)
        init = client.post(B + "/payments/initiate",
                           json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                           headers=uh).json()["data"]
        good = build_test_response(transaction_id=init["transaction_id"], amount=500)
        first = client.post(B + "/payments/verify",
                            json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": good},
                            headers=uh).json()["data"]
        second = client.post(B + "/payments/verify",
                             json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": good},
                             headers=uh).json()["data"]
        assert second["already"] is True
        assert second["ticket_code"] == first["ticket_code"]
        tickets = client.get(B + "/tickets/my", headers=uh).json()["items"]
        assert len(tickets) == 1

    def test_tampered_amount_rejected(self, client):
        from app.services.payments.esewa import build_test_response

        B, h, uh, ev, reg = _setup_paid(client)
        init = client.post(B + "/payments/initiate",
                           json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                           headers=uh).json()["data"]
        evil = build_test_response(transaction_id=init["transaction_id"], amount=1)
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": evil},
                        headers=uh)
        assert r.status_code in (400, 402)
        # still pending — honest retry works
        good = build_test_response(transaction_id=init["transaction_id"], amount=500)
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": good},
                        headers=uh)
        assert r.status_code == 200

    def test_wrong_signature_rejected(self, client):
        import base64
        import json as pyjson

        B, h, uh, ev, reg = _setup_paid(client)
        init = client.post(B + "/payments/initiate",
                           json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                           headers=uh).json()["data"]
        from app.services.payments.esewa import build_test_response

        raw = pyjson.loads(base64.b64decode(
            build_test_response(transaction_id=init["transaction_id"], amount=500)).decode())
        raw["signature"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        forged = base64.b64encode(pyjson.dumps(raw).encode()).decode()
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": forged},
                        headers=uh)
        assert r.status_code in (400, 402)

    def test_khalti_unconfigured_is_honest(self, client):
        B, h, uh, ev, reg = _setup_paid(client)
        r = client.post(B + "/payments/initiate",
                        json={"registration_id": reg["registration_id"], "provider": "KHALTI"}, headers=uh)
        assert r.status_code == 400
        assert "Khalti" in r.json().get("detail", "")

    def test_unknown_provider_rejected(self, client):
        B, h, uh, ev, reg = _setup_paid(client)
        r = client.post(B + "/payments/initiate",
                        json={"registration_id": reg["registration_id"], "provider": "PAYPAL"}, headers=uh)
        assert r.status_code == 400


class TestTransactionUuid:
    """eSewa rejects repeat transaction_uuid: every attempt mints a fresh one."""

    def test_consecutive_initiates_differ(self, client):
        import re

        B, h, uh, ev, reg = _setup_paid(client)
        first = client.post(B + "/payments/initiate",
                            json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                            headers=uh).json()["data"]
        second = client.post(B + "/payments/initiate",
                             json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                             headers=uh).json()["data"]
        assert first["transaction_id"] != second["transaction_id"]
        for txn in (first["transaction_id"], second["transaction_id"]):
            assert re.fullmatch(r"[A-Za-z0-9-]+", txn)
        assert first["transaction_id"].startswith("evt-pay-")

    def test_verify_uses_latest_attempt(self, client):
        from app.services.payments.esewa import build_test_response

        B, h, uh, ev, reg = _setup_paid(client)
        client.post(B + "/payments/initiate",
                    json={"registration_id": reg["registration_id"], "provider": "ESEWA"}, headers=uh)
        second = client.post(B + "/payments/initiate",
                             json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                             headers=uh).json()["data"]
        good = build_test_response(transaction_id=second["transaction_id"], amount=500)
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": good},
                        headers=uh)
        assert r.status_code == 200
        assert r.json()["data"]["ticket_code"].startswith("EV-")

    def test_old_attempt_superseded(self, client):
        from app.services.payments.esewa import build_test_response

        B, h, uh, ev, reg = _setup_paid(client)
        first = client.post(B + "/payments/initiate",
                            json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                            headers=uh).json()["data"]
        client.post(B + "/payments/initiate",
                    json={"registration_id": reg["registration_id"], "provider": "ESEWA"}, headers=uh)
        stale = build_test_response(transaction_id=first["transaction_id"], amount=500)
        r = client.post(B + "/payments/verify",
                        json={"registration_id": reg["registration_id"], "provider": "ESEWA", "data": stale},
                        headers=uh)
        # latest payment row carries the new uuid; stale data must not confirm it
        assert r.status_code in (400, 402)
