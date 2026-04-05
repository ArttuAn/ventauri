from __future__ import annotations

import json
from typing import Any

from agents.base import build_output, run_json_agent
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import AgentOutput, WorkflowState
from skills.branding_tools.naming import generate_name_candidates
from skills.web_tools.search import web_search_stub


def _demo_ideas(goal: str) -> dict[str, Any]:
    slug = goal.strip()[:80] or "your venture"
    return {
        "summary": f"Three differentiated directions around: {slug}",
        "ideas": [
            {
                "title": f"Vertical workflow automation for {slug.split()[0] if slug.split() else 'SMB'}",
                "score": 0.78,
                "market_size_guess": "Medium",
                "feasibility": "High",
                "competition": "Crowded; win on distribution",
                "rationale": "Pain is repetitive ops; buyers pay for measurable time saved.",
            },
            {
                "title": "Data + compliance layer as API",
                "score": 0.72,
                "market_size_guess": "Large",
                "feasibility": "Medium",
                "competition": "Moderate; win on niche regulations",
                "rationale": "Sticky once integrated; expands with partner ecosystem.",
            },
            {
                "title": "Founder-facing copilot for GTM experiments",
                "score": 0.7,
                "market_size_guess": "Growing",
                "feasibility": "High",
                "competition": "High; win on workflow depth",
                "rationale": "Aligns with Ventauri multi-agent thesis; fast iteration loops.",
            },
        ],
        "clusters": ["Automation", "Compliance / data", "GTM tooling"],
        "web_signals": web_search_stub(f"{slug} market trends"),
    }


async def run_idea_agent(
    state: WorkflowState,
    _sessions: SessionStore,
    vectors: VectorStore,
    prior: dict[str, Any],
) -> AgentOutput:
    _ = prior
    user_message = (
        f"Founder goal:\n{state.user_goal}\n\n"
        "Return JSON with keys: summary (string), ideas (array of objects with "
        "title, score 0-1, market_size_guess, feasibility, competition, rationale), "
        "clusters (string array). Optionally web_signals (object) if you infer from goal. "
        "Optionally naming_suggestions (array of {name, slug, rationale}) for product/repo names."
    )
    data, raw = await run_json_agent(
        agent_name="idea",
        prompt_name="idea_agent",
        user_message=user_message,
        demo_factory=lambda: _demo_ideas(state.user_goal),
    )
    if not data.get("naming_suggestions"):
        data["naming_suggestions"] = generate_name_candidates(state.user_goal, count=5)
    out = build_output("idea", data, raw)
    vectors.add(
        f"{state.session_id}:idea",
        json.dumps(data, ensure_ascii=False),
        {"agent": "idea", "session_id": state.session_id},
    )
    return out
