from __future__ import annotations

from typing import Any


def prd_skeleton_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = context
    return {
        "problem": goal[:400],
        "personas": prior.get("market_research", {}).get("segments", []) if isinstance(prior.get("market_research"), dict) else [],
        "non_goals": ["Breadth across many verticals before one wins"],
        "success_metrics": ["activation event", "weekly retained action", "paid conversion proxy"],
    }


def mvp_slice_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = context
    comp = prior.get("competitor_analysis", {})
    return {
        "mvp_name": "Wedge MVP",
        "must_have": [
            "Single painful job-to-be-done end-to-end",
            "Basic admin + invite",
            "Export or integration for sticky data",
        ],
        "defer": ["Full analytics", "Mobile", "Multi-tenant complexity beyond need"],
        "competitive_note": list(comp.keys())[:5] if isinstance(comp, dict) else [],
        "goal_echo": goal[:200],
    }


def roadmap_stub(*, goal: str, prior: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    _ = goal, context
    return {
        "horizons": {
            "0-30d": ["10 discovery calls", "paper prototype", "compliance questions list"],
            "30-90d": ["design partners", "narrow GA", "instrumentation baseline"],
            "90-180d": ["second workflow", "partnership pilot", "enterprise checklist"],
        },
        "dependencies": list(prior.keys()),
    }
