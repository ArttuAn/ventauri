from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from agents.base import run_json_agent
from agents.registry import active_agents, get_agent
from orchestrator.settings import get_settings
from orchestrator.telemetry import log_event

# Keyword signals → agent (weights are relative; ties broken by TIE_ORDER).
KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "compliance": [
        ("gdpr", 3.0),
        ("hipaa", 3.0),
        ("soc 2", 3.0),
        ("soc2", 3.0),
        ("compliance", 2.5),
        ("regulatory", 2.5),
        ("regulation", 2.0),
        ("legal risk", 2.5),
        ("due diligence", 2.0),
        ("diligence", 2.5),
        ("privacy policy", 2.0),
        ("data privacy", 2.5),
        ("privacy", 1.8),
        ("data protection", 2.0),
        ("subprocessor", 2.0),
        ("dpa", 1.5),
        ("dpo", 1.8),
        ("lawful basis", 2.2),
        ("enterprise pilot", 2.0),
        ("enterprise pilots", 2.0),
        ("pilot", 1.2),
        ("diligence checklist", 3.0),
        ("compliance checklist", 3.0),
    ],
    "competitor_analysis": [
        ("competitor", 2.5),
        ("competition", 2.0),
        ("differentiation", 2.0),
        ("positioning", 2.0),
        ("versus", 1.5),
        (" vs ", 1.0),
        ("landscape", 1.5),
        ("moat", 2.0),
        ("benchmark", 1.5),
    ],
    "market_research": [
        ("market sizing", 3.0),
        ("tam", 2.5),
        ("sam", 2.0),
        ("som", 2.0),
        ("market research", 2.5),
        ("segment", 2.0),
        ("icp", 2.5),
        ("persona", 2.0),
        ("customer segment", 2.0),
        ("demand", 1.5),
        ("market size", 2.5),
        ("addressable market", 2.0),
    ],
    "product_development": [
        ("prd", 3.0),
        ("mvp", 2.5),
        ("roadmap", 2.5),
        ("feature priorit", 2.0),
        ("build plan", 2.5),
        ("product scope", 2.0),
        ("user story", 2.0),
        ("sprint", 1.5),
        ("release plan", 2.0),
    ],
    "strategy": [
        ("go-to-market", 2.5),
        ("gtm", 2.5),
        ("business model", 2.5),
        ("pricing", 2.0),
        ("swot", 2.5),
        ("pitch deck", 1.5),
        ("fundraising", 1.5),
        ("unit economics", 2.0),
        ("revenue model", 2.0),
    ],
    "research": [
        ("customer interview", 2.5),
        ("user research", 2.5),
        ("trend", 1.5),
        ("hypothesis", 1.5),
        ("validate demand", 2.0),
    ],
    "idea": [
        ("brainstorm", 2.0),
        ("naming", 2.5),
        ("name for", 2.0),
        ("product name", 2.0),
        ("startup idea", 2.5),
        ("business idea", 2.0),
        ("new venture", 2.0),
    ],
}

TIE_ORDER = (
    "compliance",
    "competitor_analysis",
    "product_development",
    "market_research",
    "strategy",
    "research",
    "idea",
)

ALLOWED_CHAT_AGENT_IDS: frozenset[str] = frozenset(a.id for a in active_agents())


@dataclass
class ChatRoutingResult:
    selected_agent_id: str
    reasoning: str
    evidence: list[str]
    confidence: float
    source: str  # model | keywords | model_fallback

    def as_dict(self) -> dict:
        return asdict(self)


def _normalize_for_routing(message: str) -> str:
    """Lowercase + light typo fixes so short keywords (e.g. gdpr) still match."""
    m = message.lower().strip()
    for wrong, right in (
        ("gdptr", "gdpr"),
        ("gdrp", "gdpr"),
        ("gpdr", "gdpr"),
        ("rgdp", "gdpr"),
        ("saaas", "saas"),
        ("nefore", "before"),
    ):
        m = m.replace(wrong, right)
    return m


def _heuristic_route(message: str) -> tuple[str, list[str], float]:
    msg = _normalize_for_routing(message)
    scores: dict[str, float] = {k: 0.0 for k in KEYWORDS}
    for agent_id, pairs in KEYWORDS.items():
        for phrase, w in pairs:
            if phrase in msg:
                scores[agent_id] += w

    best = max(scores.values()) if scores else 0.0
    if best <= 0:
        evidence = [
            "No specialist keywords matched (after normalizing small typos). "
            "Using the Idea agent for open brainstorming — try words like GDPR, competitors, TAM, PRD, or GTM for a focused agent.",
        ]
        return "idea", evidence, 0.38

    tied = [a for a in TIE_ORDER if scores.get(a, 0) == best]
    chosen = tied[0]

    evidence: list[str] = []
    for phrase, w in KEYWORDS[chosen]:
        if phrase in msg:
            evidence.append(f"Matched “{phrase}” in your text (signal strength {w:.1f}) → routes to {chosen}.")
    if not evidence:
        evidence.append(f"Highest aggregate signal among agents → **{chosen}**.")

    confidence = min(0.92, 0.42 + min(best, 10.0) * 0.05)
    return chosen, evidence, confidence


def _default_reasoning(agent_id: str, evidence: list[str]) -> str:
    info = get_agent(agent_id)
    title = info.title if info else agent_id.replace("_", " ").title()
    if agent_id == "idea" and evidence and "No specialist keywords" in evidence[0]:
        return (
            "Nothing clearly pointed at one specialist, so we used the Idea agent for broad directions. "
            "Use concrete domain words if you want Compliance Agent, Market Research Agent, Competitor Analysis Agent, Product Development Agent, etc."
        )
    return (
        f"We chose {title} ({agent_id}) from the keyword signals listed below — "
        f"they’re the strongest automated match for your message right now."
    )


def _router_user_message(message: str) -> str:
    lines = [
        "Allowed agent ids (pick exactly one for `selected_agent_id`): "
        + ", ".join(f"`{x}`" for x in sorted(ALLOWED_CHAT_AGENT_IDS)),
        "",
        "Catalog:",
    ]
    for a in active_agents():
        lines.append(f"- `{a.id}`: {a.title} — {a.description}")
    lines.extend(
        [
            "",
            "Founder message:",
            message.strip(),
            "",
            "Return JSON with keys: selected_agent_id (string), reasoning (string), "
            "evidence (array of short strings quoting or paraphrasing cues from the message), "
            "confidence (number 0-1).",
        ]
    )
    return "\n".join(lines)


def _normalize_evidence(raw: Any, fallback: list[str]) -> list[str]:  # noqa: ANN401
    if not isinstance(raw, list):
        return list(fallback)
    out = [str(x).strip() for x in raw if str(x).strip()]
    return out[:12] if out else list(fallback)


async def route_chat_message(message: str) -> ChatRoutingResult:
    msg = message.strip()
    h_id, h_ev, h_conf = _heuristic_route(msg)

    def demo_factory() -> dict:
        return {
            "selected_agent_id": h_id,
            "reasoning": _default_reasoning(h_id, h_ev),
            "evidence": h_ev,
            "confidence": h_conf,
        }

    log_event(
        "chat.router",
        "route_start",
        detail={"message_chars": len(msg), "heuristic_pick": h_id},
    )

    data, _raw = await run_json_agent(
        agent_name="router",
        prompt_name="chat_router_agent",
        user_message=_router_user_message(msg),
        demo_factory=demo_factory,
    )

    if data.get("parse_error"):
        log_event(
            "chat.router",
            "llm_json_failed",
            level="warning",
            detail={"fallback": h_id},
        )
        return ChatRoutingResult(
            h_id,
            _default_reasoning(h_id, h_ev),
            h_ev,
            h_conf,
            "keywords",
        )

    rid = str(data.get("selected_agent_id", "")).strip()
    if rid not in ALLOWED_CHAT_AGENT_IDS:
        log_event(
            "chat.router",
            "invalid_agent_fallback",
            level="warning",
            detail={"returned": rid, "fallback": h_id},
        )
        return ChatRoutingResult(
            h_id,
            _default_reasoning(h_id, h_ev),
            h_ev,
            h_conf,
            "model_fallback",
        )

    reasoning = str(data.get("reasoning") or "").strip() or _default_reasoning(rid, h_ev)
    evidence = _normalize_evidence(data.get("evidence"), h_ev)

    conf_raw = data.get("confidence", h_conf)
    try:
        conf = float(conf_raw)
    except (TypeError, ValueError):
        conf = h_conf
    conf = max(0.0, min(1.0, conf))

    settings = get_settings()
    if settings.llm_enabled:
        route_source = "model"
    else:
        route_source = "keywords"
        reasoning = _default_reasoning(rid, h_ev)
        evidence = _normalize_evidence(data.get("evidence"), h_ev)
        conf = h_conf

    log_event(
        "chat.router",
        "route_done",
        detail={"selected": rid, "confidence": conf, "source": route_source},
    )

    return ChatRoutingResult(
        selected_agent_id=rid,
        reasoning=reasoning,
        evidence=evidence,
        confidence=conf,
        source=route_source,
    )
