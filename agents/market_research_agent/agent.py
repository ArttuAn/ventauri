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
        "summary": "Beachhead ICP sketched; all sizing is qualitative until you add real data sources.",
        "market_notes": "Anchor on one vertical and one measurable pain before expanding segments.",
        "tam_sam_som_hypothesis": {
            "tam": "Define category from buyer job-to-be-done",
            "sam": "Geo + segment slice you can reach in 12 months",
            "som": "First 50–200 accounts realistically",
        },
        "segments": [
            {"name": "Owner-operator", "budget_band": "low thousands ARR", "motion": "self-serve + light sales"},
            {"name": "Mid-market ops lead", "budget_band": "five figures ARR", "motion": "sales-led pilot"},
        ],
        "trends_to_monitor": ["Vendor consolidation", "AI feature parity pressure", "Proof-of-ROI expectations"],
        "open_questions": ["Willingness to pay", "Switching costs from incumbents", "Procurement steps"],
        "evidence_from_skills": ["sizing", "segments", "trends"],
    }


def _user_message(ctx: dict[str, Any]) -> str:
    return (
        f"Founder goal:\n{ctx['goal']}\n\n"
        "Return JSON with keys: summary, market_notes, tam_sam_som_hypothesis (object), "
        "segments (array of objects), trends_to_monitor (array), open_questions (array), "
        "evidence_from_skills (array).\n\n"
        f"Prior pipeline JSON:\n{json.dumps(ctx['prior'], indent=2)[:8000]}"
    )


async def run_market_research_agent(
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
        vector_doc_suffix="market_research",
    )
