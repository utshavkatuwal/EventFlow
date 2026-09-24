"""Event media upload + video_url (cover file, movie file)."""
import io
import uuid

import pytest
from fastapi.testclient import TestClient

B = "/api/v1"


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _approved_org(client):
    tag = uuid.uuid4().hex[:8]
    email = f"media_{tag}@test.com"
    otok = client.post(B + "/auth/organizer/register",
                       json={"email": email, "password": "pass1234",
                             "organization_name": "Media Org"}).json()["data"]["access_token"]
    atok = client.post(B + "/auth/login",
                       json={"email": "admin@eventflow.dev", "password": "admin123"}).json()["data"]["access_token"]
    apps = client.get(B + "/organizer-applications?status=UNDER_REVIEW",
                      headers={"Authorization": f"Bearer {atok}"}).json()["data"]
    aid = [a for a in apps if a["email"] == email][0]["id"]
    client.post(B + f"/organizer-applications/{aid}/review", json={"action": "APPROVE"},
                headers={"Authorization": f"Bearer {atok}"})
    return {"Authorization": f"Bearer {otok}"}


def _user(client):
    tag = uuid.uuid4().hex[:8]
    tok = client.post(B + "/auth/register",
                      json={"email": f"medu_{tag}@test.com", "username": f"medu_{tag}",
                            "password": "pass1234"}).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {tok}"}


PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestMediaUpload:
    def test_cover_upload_ok(self, client):
        h = _approved_org(client)
        r = client.post(B + "/events/upload?kind=cover", files={"file": ("c.png", PNG, "image/png")}, headers=h)
        assert r.status_code == 200
        assert r.json()["data"]["url"].startswith("/uploads/events/")

    def test_exe_rejected(self, client):
        h = _approved_org(client)
        r = client.post(B + "/events/upload?kind=cover",
                        files={"file": ("x.exe", b"MZ", "application/x-msdownload")}, headers=h)
        assert r.status_code == 400

    def test_video_ok_and_wrong_kind_rejected(self, client):
        h = _approved_org(client)
        r = client.post(B + "/events/upload?kind=video",
                        files={"file": ("m.mp4", b"\x00\x00\x00 ftyp" + b"0" * 100, "video/mp4")}, headers=h)
        assert r.status_code == 200
        r = client.post(B + "/events/upload?kind=video",
                        files={"file": ("c.png", PNG, "image/png")}, headers=h)
        assert r.status_code == 400

    def test_auth_required(self, client):
        uh = _user(client)
        r = client.post(B + "/events/upload?kind=cover",
                        files={"file": ("c.png", PNG, "image/png")}, headers=uh)
        assert r.status_code == 403
        assert client.post(B + "/events/upload?kind=cover",
                           files={"file": ("c.png", PNG, "image/png")}).status_code in (401, 403)

    def test_create_with_media_urls(self, client):
        h = _approved_org(client)
        up = client.post(B + "/events/upload?kind=cover",
                         files={"file": ("c.png", PNG, "image/png")}, headers=h).json()["data"]
        r = client.post(B + "/events",
                        json={"title": "Media Ev", "category_id": 4,
                              "start_date": "2027-09-01T18:00:00",
                              "cover_image_url": up["url"],
                              "video_url": "/uploads/events/fake.mp4",
                              "ticket_types": [{"name": "General", "price": 0, "capacity": 10}]},
                        headers=h)
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["cover_image_url"] == up["url"]
        assert d["video_url"] == "/uploads/events/fake.mp4"
