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
        "summary": "Compliance posture is unverified — use as a diligence checklist, not a sign-off.",
        "compliance_posture": "Preliminary — counsel required before launch commitments",
        "jurisdictions_considered": ["Unspecified — map entity + user geography"],
        "risk_register": [
            {"risk": "Privacy notice / lawful basis unclear", "severity": "medium", "mitigation": "privacy brief + DPA template review"},
            {"risk": "Subprocessor transparency", "severity": "medium", "mitigation": "maintain subprocessor register"},
        ],
        "obligations": [
            {"item": "Document DPIA if high-risk processing (EU context)", "owner": "founder + counsel"},
        ],
        "disclaimers": [
            "This output is not legal advice. Engage qualified counsel for your jurisdictions and facts.",
        ],
        "next_verification_steps": ["Data map", "Jurisdiction pick", "Counsel intake call"],
        "evidence_from_skills": ["regulatory_scan", "obligation_matrix"],
    }


def _user_message(ctx: dict[str, Any]) -> str:
    return (
        f"Founder goal:\n{ctx['goal']}\n\n"
        "Return JSON with keys: summary, compliance_posture, jurisdictions_considered (array), "
        "risk_register (array of objects with risk, severity, mitigation), obligations (array), "
        "disclaimers (array of strings), next_verification_steps (array), evidence_from_skills (array).\n\n"
        f"Prior pipeline JSON (other agents may be empty on first stage):\n{json.dumps(ctx['prior'], indent=2)[:8000]}"
    )


async def run_compliance_agent(
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
        vector_doc_suffix="compliance",
    )
