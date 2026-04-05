from __future__ import annotations

import json
from typing import Any

from agents.base import build_output, run_json_agent
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import AgentOutput, WorkflowState


def _demo_strategy(
    goal: str,
    idea_payload: dict[str, Any],
    research_payload: dict[str, Any],
) -> dict[str, Any]:
    ideas = idea_payload.get("ideas") or []
    top = ideas[0].get("title", "Primary concept") if ideas else goal[:100]
    return {
        "summary": f"Focus first on: {top}",
        "recommended_focus": top,
        "business_model_sketch": "Land with wedge workflow; expand seats via integrations; annual contracts after ROI proof.",
        "pricing_hypothesis": "Starter self-serve; pro seat-based; enterprise with SSO + SLA.",
        "gtm_first_90_days": [
            "10 problem discovery interviews in one vertical",
            "Ship narrow MVP that removes one painful weekly task",
            "3 design-partner LOIs before broad marketing",
        ],
        "swot": {
            "strengths": ["Speed", "Vertical focus"],
            "weaknesses": ["Brand", "Services load"],
            "opportunities": ["Regulatory tailwinds", "API partners"],
            "threats": ["Incumbent bundling", "Commoditized LLM features"],
        },
        "risks": ["Long enterprise sales", "Integration fragility"],
        "research_echo": (research_payload.get("summary") or "")[:200],
    }


async def run_strategy_agent(
    state: WorkflowState,
    _sessions: SessionStore,
    vectors: VectorStore,
    prior: dict[str, Any],
) -> AgentOutput:
    idea_payload = prior.get("idea") or {}
    research_payload = prior.get("research") or {}
    user_message = (
        f"Founder goal:\n{state.user_goal}\n\n"
        f"Ideas JSON:\n{json.dumps(idea_payload, indent=2)[:4000]}\n\n"
        f"Research JSON:\n{json.dumps(research_payload, indent=2)[:4000]}\n\n"
        "Return JSON with keys: summary, recommended_focus, business_model_sketch, "
        "pricing_hypothesis, gtm_first_90_days (string array), swot (object), risks (string array)."
    )
    data, raw = await run_json_agent(
        agent_name="strategy",
        prompt_name="strategy_agent",
        user_message=user_message,
        demo_factory=lambda: _demo_strategy(state.user_goal, idea_payload, research_payload),
    )
    out = build_output("strategy", data, raw)
    vectors.add(
        f"{state.session_id}:strategy",
        json.dumps(data, ensure_ascii=False),
        {"agent": "strategy", "session_id": state.session_id},
    )
    return out
