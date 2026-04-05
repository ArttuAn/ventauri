from __future__ import annotations

from typing import Any


def sizing_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = prior, context
    return {
        "tam_sam_som": {
            "tam": "Qualitative — define category boundary from goal",
            "sam": "Beachhead geography + segment cut",
            "som": "Year-1 reachable with current GTM",
        },
        "assumptions": ["No verified figures — replace with paid data / filings"],
        "goal_echo": goal[:200],
    }


def segment_map_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = context
    comp = prior.get("compliance", {}) if isinstance(prior.get("compliance"), dict) else {}
    return {
        "segments": [
            {"name": "Primary economic buyer", "criteria": "budget authority + pain owner"},
            {"name": "Champion user", "criteria": "daily workflow embed"},
            {"name": "IT / security gate", "criteria": "depends on data sensitivity"},
        ],
        "compliance_hooks": list(comp.keys())[:5] if comp else [],
    }


def trend_pulse_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = goal, prior, context
    return {
        "signals": [
            "Buyers demand ROI proof within one sales cycle",
            "Vertical SaaS wins on workflow depth vs horizontal breadth",
            "AI features commoditize — differentiation is data + workflow",
        ],
        "sources": ["stub://ventauri.market/pulse"],
    }
