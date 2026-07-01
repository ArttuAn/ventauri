from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from api.repo import save_workflow_result
from memory.session_store import SessionStore
from orchestrator.models import WorkflowState
from orchestrator.router import route_user_goal
from orchestrator.runner import PIPELINE_STAGE_IDS, PipelineRunner
from orchestrator.telemetry import log_event, telemetry_scope


def resolve_pipeline(goal: str, pipeline: str | None) -> tuple[str, str]:
    """Return (pipeline_id, route_reason). Raises ValueError for unknown explicit pipeline."""
    if pipeline:
        if pipeline not in PIPELINE_STAGE_IDS:
            known = ", ".join(sorted(PIPELINE_STAGE_IDS))
            raise ValueError(f"Unknown pipeline {pipeline!r}. Valid: {known}")
        return pipeline, "client-selected pipeline"
    decision = route_user_goal(goal)
    return decision.pipeline_id, decision.reason


async def run_venture_workflow(
    *,
    goal: str,
    pipeline: str | None,
    runner: PipelineRunner,
    memory_sessions: SessionStore,
    db: AsyncSession,
    job_id: str | None = None,
) -> dict[str, Any]:
    pipeline_id, reason = resolve_pipeline(goal, pipeline)

    state = WorkflowState(user_goal=goal)
    async with telemetry_scope(job_id=job_id, session_id=state.session_id, pipeline_id=pipeline_id):
        log_event(
            "workflow",
            "dispatch",
            detail={
                "pipeline_id": pipeline_id,
                "route_reason": reason,
                "goal_chars": len(goal),
                "explicit_pipeline": pipeline is not None,
            },
        )
        memory_sessions.save(state)
        outputs = await runner.run_pipeline(state, pipeline_id)
        stages = [s for s, _ in runner.stages_for(pipeline_id)]
        log_event(
            "workflow",
            "sqlite_persist_start",
            detail={"session_id": state.session_id, "report_rows": len(outputs)},
        )
        await save_workflow_result(db, state, reason, outputs, stages)
        log_event("workflow", "sqlite_persist_done", detail={"session_id": state.session_id})

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
