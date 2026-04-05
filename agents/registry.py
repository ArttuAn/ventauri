from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentInfo:
    id: str
    title: str
    description: str
    status: str  # active | planned
    icon: str
    pipelines: tuple[str, ...]
    harness: str  # path hint for developers


AGENTS: tuple[AgentInfo, ...] = (
    AgentInfo(
        id="compliance",
        title="Law & regulation compliance",
        description="Harness: rules + compliance skills + session-scoped memory. Surfaces diligence questions, not legal advice.",
        status="active",
        icon="⚖️",
        pipelines=("venture-intelligence",),
        harness="agents/compliance_agent/",
    ),
    AgentInfo(
        id="market_research",
        title="Market research",
        description="Harness: sizing/segment/trend skills + memory. Segments, motions, and hypotheses without fake statistics.",
        status="active",
        icon="📈",
        pipelines=("venture-intelligence",),
        harness="agents/market_research_agent/",
    ),
    AgentInfo(
        id="competitor_analysis",
        title="Competitor analysis",
        description="Harness: landscape + differentiation skills + memory. Archetypes and positioning safe for public data.",
        status="active",
        icon="🎯",
        pipelines=("venture-intelligence",),
        harness="agents/competitor_analysis_agent/",
    ),
    AgentInfo(
        id="product_development",
        title="Product development",
        description="Harness: PRD/MVP/roadmap skills + memory. Scope, non-goals, and metrics grounded in prior stages.",
        status="active",
        icon="🛠️",
        pipelines=("venture-intelligence",),
        harness="agents/product_development_agent/",
    ),
    AgentInfo(
        id="idea",
        title="Idea",
        description="Generates and scores business ideas, clusters themes, suggests naming directions.",
        status="active",
        icon="💡",
        pipelines=("idea-to-strategy",),
        harness="agents/idea_agent/",
    ),
    AgentInfo(
        id="research",
        title="Research (strategy pipeline)",
        description="Market notes, personas, competitors, and trend hypotheses tied to your goal.",
        status="active",
        icon="🔍",
        pipelines=("idea-to-strategy",),
        harness="agents/research_agent/",
    ),
    AgentInfo(
        id="strategy",
        title="Strategy",
        description="Business model sketch, pricing hypothesis, GTM 90-day plan, SWOT, risks.",
        status="active",
        icon="📊",
        pipelines=("idea-to-strategy",),
        harness="agents/strategy_agent/",
    ),
    AgentInfo(
        id="validation",
        title="Validation",
        description="Experiments, landing pages, interviews, and signal interpretation (planned).",
        status="planned",
        icon="🧪",
        pipelines=(),
        harness="agents/validation_agent/",
    ),
    AgentInfo(
        id="marketing",
        title="Marketing",
        description="Content, SEO, social, copy (planned).",
        status="planned",
        icon="📣",
        pipelines=(),
        harness="agents/marketing_agent/",
    ),
    AgentInfo(
        id="finance",
        title="Finance",
        description="Projections, burn, unit economics (planned).",
        status="planned",
        icon="💰",
        pipelines=(),
        harness="agents/finance_agent/",
    ),
    AgentInfo(
        id="growth",
        title="Growth",
        description="Funnels, A/B tests, retention (planned).",
        status="planned",
        icon="📉",
        pipelines=(),
        harness="agents/growth_agent/",
    ),
    AgentInfo(
        id="ops",
        title="Ops",
        description="Hiring, processes, tool stack (planned).",
        status="planned",
        icon="🧑‍💼",
        pipelines=(),
        harness="agents/ops_agent/",
    ),
)


def get_agent(agent_id: str) -> AgentInfo | None:
    for a in AGENTS:
        if a.id == agent_id:
            return a
    return None


def active_agents() -> list[AgentInfo]:
    return [a for a in AGENTS if a.status == "active"]


def planned_agents() -> list[AgentInfo]:
    return [a for a in AGENTS if a.status == "planned"]
