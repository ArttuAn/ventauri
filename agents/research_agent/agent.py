from __future__ import annotations

import json
from typing import Any

from agents.base import build_output, run_json_agent
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import AgentOutput, WorkflowState
from skills.data_tools.trends import trend_stub


def _demo_research(goal: str, idea_payload: dict[str, Any]) -> dict[str, Any]:
    titles = [i.get("title", "") for i in idea_payload.get("ideas", [])][:3]
    focus = titles[0] if titles else goal[:120]
    return {
        "summary": f"Landscape scan for: {focus}",
        "market_notes": (
            "Buyers optimize for ROI within two sales cycles; wedge features beat broad suites early."
        ),
        "personas": [
            {"name": "Operator GM", "pains": ["throughput", "hiring"], "budget": "3-15k MRR"},
            {"name": "Technical lead", "pains": ["integration", "reliability"], "budget": "pilot-first"},
        ],
        "competitors": [
            {"name": "Incumbent A", "angle": "Legacy suite; slow innovation"},
            {"name": "Startup B", "angle": "PLG; shallow enterprise features"},
        ],
        "trends": trend_stub(focus or goal),
        "idea_context": titles,
    }


async def run_research_agent(
    state: WorkflowState,
    _sessions: SessionStore,
    vectors: VectorStore,
    prior: dict[str, Any],
) -> AgentOutput:
    idea_payload = prior.get("idea") or {}
    user_message = (
        f"Founder goal:\n{state.user_goal}\n\n"
        f"Prior idea agent JSON:\n{json.dumps(idea_payload, indent=2)[:6000]}\n\n"
        "Return JSON with keys: summary, market_notes, personas (array of objects), "
        "competitors (array with name, angle), trends (string array), idea_context (string array)."
    )
    data, raw = await run_json_agent(
        agent_name="research",
        prompt_name="research_agent",
        user_message=user_message,
        demo_factory=lambda: _demo_research(state.user_goal, idea_payload),
    )
    out = build_output("research", data, raw)
    vectors.add(
        f"{state.session_id}:research",
        json.dumps(data, ensure_ascii=False),
        {"agent": "research", "session_id": state.session_id},
    )
    return out
