import pytest

from api.run_service import resolve_pipeline


def test_resolve_pipeline_auto_route() -> None:
    pid, reason = resolve_pipeline("B2B SaaS for clinics", None)
    assert pid == "idea-to-strategy"
    assert reason


def test_resolve_pipeline_explicit_valid() -> None:
    pid, reason = resolve_pipeline("anything", "venture-intelligence")
    assert pid == "venture-intelligence"
    assert "client" in reason


def test_resolve_pipeline_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown pipeline"):
        resolve_pipeline("goal", "not-a-pipeline")
