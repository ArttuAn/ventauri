from fastapi.testclient import TestClient

from api.main import app
from orchestrator.telemetry import get_events, log_event


def test_log_and_get_events() -> None:
    n = log_event("test", "ping", detail={"k": 1})
    ev = get_events(since_id=n - 1, limit=10)
    assert any(e["message"] == "ping" for e in ev)


def test_api_activity_empty_ok() -> None:
    with TestClient(app) as c:
        r = c.get("/api/activity")
        assert r.status_code == 200
        assert "events" in r.json()


def test_api_job_unknown_404() -> None:
    with TestClient(app) as c:
        r = c.get("/api/jobs/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404
