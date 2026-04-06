"""Heuristic routing signals for dashboard chat."""

from __future__ import annotations

import pytest

from orchestrator.chat_router import _heuristic_route


@pytest.mark.parametrize(
    ("msg", "expected_agent"),
    [
        ("We need GDPR and a DPA before enterprise deals", "compliance"),
        ("TAM SAM SOM for our ICP and personas", "market_research"),
        ("How do we differentiate vs CompetitorX", "competitor_analysis"),
        ("PRD and roadmap for the MVP scope", "product_development"),
        ("SWOT and pricing for GTM", "strategy"),
        ("Customer interviews to validate demand", "research"),
        ("Brainstorm startup names for our AI copilot", "idea"),
        (
            "draft a gdptr diligence checklist for our b2b saaas nefore enterprise pilots",
            "compliance",
        ),
        ("Need a diligence checklist before enterprise pilots", "compliance"),
    ],
)
def test_heuristic_route_domain(msg: str, expected_agent: str) -> None:
    agent_id, evidence, conf = _heuristic_route(msg)
    assert agent_id == expected_agent
    assert evidence
    assert 0 <= conf <= 1


def test_heuristic_default_idea() -> None:
    agent_id, evidence, conf = _heuristic_route("hello world")
    assert agent_id == "idea"
    assert conf < 0.5
    assert evidence and "No specialist keywords" in evidence[0]
