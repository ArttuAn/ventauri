from __future__ import annotations

import json
from typing import Any, Callable

from orchestrator.llm import complete_chat, parse_json_block
from orchestrator.models import AgentOutput
from orchestrator.prompt_loader import load_prompt
from orchestrator.settings import get_settings


async def run_json_agent(
    *,
    agent_name: str,
    prompt_name: str,
    user_message: str,
    demo_factory: dict[str, Any] | Callable[[], dict[str, Any]],
) -> tuple[dict[str, Any], str]:
    system = load_prompt(prompt_name) or f"You are the {agent_name} for Ventauri. Respond with JSON only."
    settings = get_settings()
    if settings.llm_enabled:
        raw = await complete_chat(system, user_message)
        try:
            return parse_json_block(raw), raw
        except json.JSONDecodeError:
            return {"parse_error": True, "raw": raw}, raw
    data = demo_factory() if callable(demo_factory) else demo_factory
    return data, json.dumps(data, indent=2)


def build_output(agent_name: str, data: dict[str, Any], raw: str) -> AgentOutput:
    summary = data.get("summary") or data.get("recommended_focus") or data.get("market_notes") or ""
    if isinstance(summary, list):
        summary = "; ".join(str(x) for x in summary[:3])
    summary = str(summary)[:500]
    return AgentOutput(
        agent_name=agent_name,
        summary=summary or f"{agent_name} completed",
        structured=data,
        raw_text=raw,
    )
