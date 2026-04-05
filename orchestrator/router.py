from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    pipeline_id: str
    reason: str


def route_user_goal(goal: str) -> RouteDecision:
    """Pick a default pipeline from free-text goal (light heuristics)."""
    g = goal.lower()
    if any(k in g for k in ("validate", "experiment", "mvp test", "landing page")):
        return RouteDecision("idea-to-strategy", "goal mentions validation-style language")
    if any(k in g for k in ("saas", "b2b", "startup", "business", "idea")):
        return RouteDecision("idea-to-strategy", "general venture / product language")
    return RouteDecision("idea-to-strategy", "default pipeline")
