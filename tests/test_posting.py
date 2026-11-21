import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import Platform, PlatformError
from app.services import posting_service

client = TestClient(app)
OK = "Check out our latest business platform and grow your online visibility. https://example.com"


# ---------- validation ----------
@pytest.mark.parametrize("msg,fragment", [
    ("x" * 201 + " https://a.com", "exceed 200"),
    ("no link here", "none found"),
    ("two https://a.com and https://b.com", "2 found"),
    ("bad link https://not_a_url", "not a valid URL"),
    ("www.example.com no scheme", "http://"),
    ("   ", "empty"),
])
def test_invalid_messages(msg, fragment):
    r = client.post("/posting", json={"message": msg})
    assert r.status_code == 422
    assert fragment in r.json()["errors"][0]["message"]


def test_missing_field():
    assert client.post("/posting", json={}).status_code == 422


# ---------- orchestration ----------
class Good(Platform):
    name = "Good"
    async def publish(self, c, m, l): return "https://example.com/post/1"

class Bad(Platform):
    name = "Bad"
    async def publish(self, c, m, l): raise PlatformError("boom")

class Crash(Platform):
    name = "Crash"
    async def publish(self, c, m, l): raise RuntimeError("unexpected")

class NoCreds(Good):
    name = "NoCreds"
    required_settings = ["nope"]


def test_one_failure_does_not_stop_others(monkeypatch):
    async def public(*a, **k): return True
    monkeypatch.setattr(posting_service, "_is_public", public)
    creds = type("S", (), {"nope": ""})()
    monkeypatch.setattr(posting_service, "get_platforms",
                        lambda: [Good(None), Bad(None), Crash(None), NoCreds(creds)])
    r = client.post("/posting", json={"message": OK})
    assert r.status_code == 200
    body = r.json()
    by = {x["platform"]: x for x in body["results"]}
    assert body["success"] is True
    assert by["Good"]["status"] == "success" and by["Good"]["public_access"] is True
    assert by["Bad"]["error"] == "boom"
    assert "Unexpected error" in by["Crash"]["error"]
    assert "missing credentials" in by["NoCreds"]["error"]
