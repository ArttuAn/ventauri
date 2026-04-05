from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents.harness.executor import run_harnessed_turn
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import AgentOutput, WorkflowState

_DIR = Path(__file__).resolve().parent


def _demo() -> dict[str, Any]:
    return {
        "summary": "Competitive landscape framed as archetypes; validate with customer interviews and win/loss.",
        "competitor_archetypes": [
            {"name": "Legacy suite", "strength": "trust + breadth", "weakness": "slow iteration"},
            {"name": "PLG point tool", "strength": "fast adoption", "weakness": "enterprise gaps"},
        ],
        "positioning_hypothesis": "Win a narrow workflow with measurable ROI, then expand surface area.",
        "differentiation_axes": [
            {"axis": "Time-to-value vs enterprise depth", "where_you_play": "fast TTV in one vertical"},
        ],
        "watch_list": ["Incumbent bundling", "Open-source substitutes", "Feature parity on AI"],
        "evidence_from_skills": ["peer_landscape", "differentiation_grid"],
    }


def _user_message(ctx: dict[str, Any]) -> str:
    return (
        f"Founder goal:\n{ctx['goal']}\n\n"
        "Return JSON with keys: summary, competitor_archetypes (array of objects), "
        "positioning_hypothesis (string), differentiation_axes (array), watch_list (array), "
        "evidence_from_skills (array).\n\n"
        f"Prior pipeline JSON:\n{json.dumps(ctx['prior'], indent=2)[:8000]}"
    )


async def run_competitor_analysis_agent(
    state: WorkflowState,
    sessions: SessionStore,
    vectors: VectorStore,
    prior: dict[str, Any],
) -> AgentOutput:
    return await run_harnessed_turn(
        harness_dir=_DIR,
        state=state,
        _sessions=sessions,
        vectors=vectors,
        prior=prior,
        demo_factory=_demo,
        user_message_fn=_user_message,
        vector_doc_suffix="competitor_analysis",
    )
