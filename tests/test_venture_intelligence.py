import pytest

from agents.harness.loader import load_harness_spec
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import WorkflowState
from orchestrator.router import route_user_goal
from orchestrator.runner import PipelineRunner
from pathlib import Path


def test_route_venture_intelligence_for_compliance_keywords() -> None:
    r = route_user_goal("We need GDPR compliance for our EU health app")
    assert r.pipeline_id == "venture-intelligence"


@pytest.mark.asyncio
async def test_venture_intelligence_pipeline_four_agents() -> None:
    runner = PipelineRunner(SessionStore(), VectorStore())
    state = WorkflowState(user_goal="B2B analytics with HIPAA and competitor benchmarking")
    outs = await runner.run_pipeline(state, "venture-intelligence")
    names = [o.agent_name for o in outs]
    assert names == ["compliance", "market_research", "competitor_analysis", "product_development"]


def test_load_compliance_harness_spec() -> None:
    path = Path(__file__).resolve().parents[1] / "agents" / "compliance_agent" / "harness.yaml"
    spec = load_harness_spec(path)
    assert spec.agent_id == "compliance"
    assert len(spec.skill_bindings) >= 1
