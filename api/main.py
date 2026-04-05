from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import WorkflowState
from orchestrator.router import route_user_goal
from orchestrator.runner import PIPELINE_STAGE_IDS, PipelineRunner

app = FastAPI(
    title="FounderOS API",
    version="0.1.0",
    description="Multi-agent orchestration for founder workflows",
)

_sessions = SessionStore()
_vectors = VectorStore()
_runner = PipelineRunner(_sessions, _vectors)


class RunRequest(BaseModel):
    goal: str
    pipeline: str | None = Field(
        default=None,
        description="Pipeline id, e.g. idea-to-strategy. Auto-routed when omitted.",
    )


class RunResponse(BaseModel):
    session_id: str
    pipeline_id: str
    route_reason: str
    outputs: list[dict[str, Any]]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/pipelines")
def pipelines() -> dict[str, list[str]]:
    return PIPELINE_STAGE_IDS


@app.post("/run", response_model=RunResponse)
async def run_pipeline(req: RunRequest) -> RunResponse:
    decision = route_user_goal(req.goal) if not req.pipeline else None
    pipeline_id = req.pipeline or (decision.pipeline_id if decision else "idea-to-strategy")
    reason = decision.reason if decision else "client-selected pipeline"

    state = WorkflowState(user_goal=req.goal)
    _sessions.save(state)
    outs = await _runner.run_pipeline(state, pipeline_id)
    return RunResponse(
        session_id=state.session_id,
        pipeline_id=pipeline_id,
        route_reason=reason,
        outputs=[
            {
                "agent": o.agent_name,
                "summary": o.summary,
                "structured": o.structured,
            }
            for o in outs
        ],
    )
