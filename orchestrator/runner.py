from __future__ import annotations

from typing import Any, Awaitable, Callable

from agents.idea_agent.agent import run_idea_agent
from agents.research_agent.agent import run_research_agent
from agents.strategy_agent.agent import run_strategy_agent
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import AgentOutput, WorkflowState
from workflows.idea_to_strategy import STAGES as IDEA_TO_STRATEGY_STAGES

StageFn = Callable[
    [WorkflowState, SessionStore, VectorStore, dict[str, Any]],
    Awaitable[AgentOutput],
]

_REGISTRY: dict[str, list[tuple[str, StageFn]]] = {
    "idea-to-strategy": [
        ("idea", run_idea_agent),
        ("research", run_research_agent),
        ("strategy", run_strategy_agent),
    ],
}


class PipelineRunner:
    def __init__(self, sessions: SessionStore, vectors: VectorStore) -> None:
        self.sessions = sessions
        self.vectors = vectors

    def stages_for(self, pipeline_id: str) -> list[tuple[str, StageFn]]:
        return _REGISTRY.get(pipeline_id, _REGISTRY["idea-to-strategy"])

    async def run_pipeline(self, state: WorkflowState, pipeline_id: str) -> list[AgentOutput]:
        state.pipeline_id = pipeline_id
        state.stage = "running"
        state.append_event("pipeline_started", {"pipeline_id": pipeline_id})
        self.sessions.save(state)

        outputs: list[AgentOutput] = []
        prior: dict[str, Any] = {}
        for stage_name, fn in self.stages_for(pipeline_id):
            state.stage = stage_name
            state.append_event("stage_started", {"stage": stage_name})
            out = await fn(state, self.sessions, self.vectors, prior)
            prior[stage_name] = out.structured
            outputs.append(out)
            state.append_event(
                "stage_completed",
                {"stage": stage_name, "agent": out.agent_name, "summary": out.summary},
            )
            self.sessions.save(state)

        state.stage = "completed"
        state.append_event("pipeline_completed", {"pipeline_id": pipeline_id})
        self.sessions.save(state)
        return outputs


# Export stage IDs for docs / CLI
PIPELINE_STAGE_IDS = {k: [s for s, _ in v] for k, v in _REGISTRY.items()}
__all__ = ["PipelineRunner", "PIPELINE_STAGE_IDS", "IDEA_TO_STRATEGY_STAGES"]
