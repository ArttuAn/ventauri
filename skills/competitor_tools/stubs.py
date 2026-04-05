from __future__ import annotations

from typing import Any


def peer_landscape_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = context
    mr = prior.get("market_research", {}) if isinstance(prior.get("market_research"), dict) else {}
    return {
        "categories": ["Incumbent suite", "Point solution startups", "Open-source DIY"],
        "example_peers": [
            {"archetype": "Legacy incumbent", "risk": "bundling", "wedge": "narrow workflow"},
            {"archetype": "PLG native", "risk": "shallow enterprise", "wedge": "SSO + audit logs"},
        ],
        "market_context_keys": list(mr.keys())[:8],
        "goal_echo": goal[:160],
    }


def differentiation_grid_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = context
    return {
        "axes": [
            {"x": "Time-to-value", "y": "Enterprise depth"},
            {"x": "Price", "y": "Compliance posture"},
        ],
        "hypothesis": "Win on time-to-value in one vertical while meeting minimum enterprise bar",
        "prior_stages": list(prior.keys()),
        "goal_echo": goal[:120],
    }
