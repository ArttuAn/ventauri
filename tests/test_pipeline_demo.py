import asyncio

from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import WorkflowState
from orchestrator.runner import PipelineRunner


def test_pipeline_runs_three_agents() -> None:
    async def _run() -> None:
        runner = PipelineRunner(SessionStore(), VectorStore())
        state = WorkflowState(user_goal="Demo SaaS for dentists")
        outs = await runner.run_pipeline(state, "idea-to-strategy")
        assert [o.agent_name for o in outs] == ["idea", "research", "strategy"]
        assert state.stage == "completed"

    asyncio.run(_run())
