from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from api.repo import save_workflow_result
from memory.session_store import SessionStore
from orchestrator.models import WorkflowState
from orchestrator.router import route_user_goal
from orchestrator.runner import PipelineRunner


async def run_venture_workflow(
    *,
    goal: str,
    pipeline: str | None,
    runner: PipelineRunner,
    memory_sessions: SessionStore,
    db: AsyncSession,
) -> dict[str, Any]:
    decision = route_user_goal(goal) if not pipeline else None
    pipeline_id = pipeline or (decision.pipeline_id if decision else "idea-to-strategy")
    reason = decision.reason if decision else "client-selected pipeline"

    state = WorkflowState(user_goal=goal)
    memory_sessions.save(state)
    outputs = await runner.run_pipeline(state, pipeline_id)
    stages = [s for s, _ in runner.stages_for(pipeline_id)]
    await save_workflow_result(db, state, reason, outputs, stages)

    return {
        "session_id": state.session_id,
        "pipeline_id": pipeline_id,
        "route_reason": reason,
        "outputs": [
            {
                "agent": o.agent_name,
                "summary": o.summary,
                "structured": o.structured,
            }
            for o in outputs
        ],
    }
