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
        "summary": "MVP slice defined around one workflow; roadmap sequenced for learning before scale.",
        "mvp": {
            "name": "Wedge MVP",
            "must_have": ["Core job end-to-end", "Basic admin", "Minimum trust signals"],
            "explicit_non_goals": ["Multi-vertical parity", "Full analytics suite"],
        },
        "roadmap": {
            "0_30d": ["Customer discovery", "clickable prototype", "compliance question list"],
            "30_90d": ["Design partner build", "instrumentation", "first paid pilot"],
        },
        "risks": ["Scope creep", "Enterprise asks before beachhead lock", "Underestimating integrations"],
        "metrics": ["activation definition", "weekly retained action", "pilot NPS / depth"],
        "evidence_from_skills": ["prd_skeleton", "mvp_slice", "roadmap"],
    }


def _user_message(ctx: dict[str, Any]) -> str:
    return (
        f"Founder goal:\n{ctx['goal']}\n\n"
        "Return JSON with keys: summary, mvp (object with name, must_have array, explicit_non_goals array), "
        "roadmap (object with string keys for horizons), risks (array), metrics (array), "
        "evidence_from_skills (array).\n\n"
        f"Prior pipeline JSON:\n{json.dumps(ctx['prior'], indent=2)[:8000]}"
    )


async def run_product_development_agent(
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
        vector_doc_suffix="product_development",
    )
