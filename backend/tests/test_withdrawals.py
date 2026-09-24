"""Phase 7 regression: withdrawals, exact ledger, admin payout."""
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _funded(client):
    """Approved organizer with Rs.480 settled available (one Rs.500 ticket)."""
    from app.services.payments.esewa import build_test_response

    tag = uuid.uuid4().hex[:8]
    B = "/api/v1"
    otok = client.post(B + "/auth/organizer/register",
                       json={"email": f"w7_{tag}@test.com", "password": "pass1234",
                             "organization_name": "W7 Org"}).json()["data"]["access_token"]
    atok = client.post(B + "/auth/login",
                       json={"email": "admin@eventflow.dev", "password": "admin123"}).json()["data"]["access_token"]
    apps = client.get(B + "/organizer-applications?status=UNDER_REVIEW",
                      headers={"Authorization": f"Bearer {atok}"}).json()["data"]
    aid = [a for a in apps if a["email"] == f"w7_{tag}@test.com"][0]["id"]
    client.post(B + f"/organizer-applications/{aid}/review", json={"action": "APPROVE"},
                headers={"Authorization": f"Bearer {atok}"})
    h = {"Authorization": f"Bearer {otok}"}
    A = {"Authorization": f"Bearer {atok}"}
    ev = client.post(B + "/events",
                     json={"title": f"W7 {tag}", "category_id": 4,
                           "start_date": "2027-09-01T18:00:00", "end_date": "2027-09-01T20:00:00",
                           "max_capacity": 50, "price_min": 500}, headers=h).json()["data"]
    client.patch(B + f"/events/{ev['id']}/publish", headers=h)
    tt = client.get(B + f"/events/{ev['id']}/tickets").json()["items"][0]
    utok = client.post(B + "/auth/register",
                       json={"email": f"w7u_{tag}@test.com", "username": f"w7u_{tag}",
                             "password": "pass1234"}).json()["data"]["access_token"]
    uh = {"Authorization": f"Bearer {utok}"}
    reg = client.post(B + "/registrations", json={"event_id": ev["id"], "ticket_type_id": tt["id"]},
                      headers=uh).json()["data"]
    init = client.post(B + "/payments/initiate",
                       json={"registration_id": reg["registration_id"], "provider": "ESEWA"},
                       headers=uh).json()["data"]
    client.post(B + "/payments/verify",
                json={"registration_id": reg["registration_id"], "provider": "ESEWA",
                      "data": build_test_response(transaction_id=init["transaction_id"], amount=500)},
                headers=uh)
    past = (datetime.utcnow() - timedelta(days=5)).isoformat()
    client.put(B + f"/events/{ev['id']}", json={"end_date": past}, headers=h)
    wallet = client.get(B + "/organizer/wallet", headers=h).json()["data"]
    assert wallet["available_balance"] == 480.0
    return B, h, A, ev


class TestWithdrawals:
    def test_request_and_pay_exact(self, client):
        B, h, A, ev = _funded(client)
        r = client.post(B + "/withdrawals",
                        json={"provider": "ESEWA", "account_number": "9841000000", "amount": 200}, headers=h)
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["service_fee"] == 20.0 and d["payout_amount"] == 180.0
        wid = d["id"]
        # admin sees it pending
        pending = client.get(B + "/withdrawals?status=PENDING", headers=A).json()["items"]
        assert any(w["id"] == wid for w in pending)
        # pay requires reference
        assert client.post(B + f"/withdrawals/{wid}/pay", json={}, headers=A).status_code == 400
        r = client.post(B + f"/withdrawals/{wid}/pay",
                        json={"transaction_reference": "ESEWA-REF-1"}, headers=A)
        assert r.status_code == 200
        wallet = client.get(B + "/organizer/wallet", headers=h).json()["data"]
        assert wallet["available_balance"] == 280.0
        kinds = {t["type"] for t in wallet["transactions"]}
        assert "WITHDRAWAL" in kinds
        # double pay blocked
        assert client.post(B + f"/withdrawals/{wid}/pay",
                           json={"transaction_reference": "X"}, headers=A).status_code == 400

    def test_over_request_blocked(self, client):
        B, h, A, ev = _funded(client)
        assert client.post(B + "/withdrawals",
                           json={"provider": "KHALTI", "account_number": "9800000001", "amount": 5000},
                           headers=h).status_code == 400
        # below fee blocked
        assert client.post(B + "/withdrawals",
                           json={"provider": "ESEWA", "account_number": "9800000001", "amount": 10},
                           headers=h).status_code == 400

    def test_reject_needs_reason(self, client):
        B, h, A, ev = _funded(client)
        wid = client.post(B + "/withdrawals",
                          json={"provider": "ESEWA", "account_number": "9841000000", "amount": 100},
                          headers=h).json()["data"]["id"]
        assert client.post(B + f"/withdrawals/{wid}/reject", json={}, headers=A).status_code == 400
        assert client.post(B + f"/withdrawals/{wid}/reject", json={"admin_note": "bad docs"},
                           headers=A).status_code == 200
        # rejected: balance untouched
        assert client.get(B + "/organizer/wallet", headers=h).json()["data"]["available_balance"] == 480.0

    def test_stranger_cannot_request(self, client):
        B, h, A, ev = _funded(client)
        utok = client.post(B + "/auth/register",
                           json={"email": f"w7s_{uuid.uuid4().hex[:8]}@test.com",
                                 "username": f"w7s_{uuid.uuid4().hex[:8]}", "password": "pass1234"}
                           ).json()["data"]["access_token"]
        assert client.post(B + "/withdrawals",
                           json={"provider": "ESEWA", "account_number": "1", "amount": 10},
                           headers={"Authorization": f"Bearer {utok}"}).status_code == 403
