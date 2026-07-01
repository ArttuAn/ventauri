from fastapi.testclient import TestClient

from api.main import app


def test_api_chat_routes_and_returns_agent() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/chat",
            json={"message": "Draft a GDPR diligence checklist for our B2B SaaS before enterprise pilots"},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["routing"]["selected_agent_id"] == "compliance"
        assert data["routing"]["agent_title"] == "Compliance Agent"
        assert data["agent_output"]["agent_display_title"] == "Compliance Agent"
        assert data["agent_output"]["summary"]


def test_health_reports_db_and_llm_mode() -> None:
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["db"] == "ok"
        assert body["llm"] in ("demo", "enabled")
        assert body["status"] in ("ok", "degraded")
