from __future__ import annotations

import json
from typing import Any, Callable

from orchestrator.llm import complete_chat, parse_json_block
from orchestrator.models import AgentOutput
from orchestrator.prompt_loader import load_prompt
from orchestrator.settings import get_settings
from orchestrator.telemetry import log_event


async def run_json_agent(
    *,
    agent_name: str,
    prompt_name: str,
    user_message: str,
    demo_factory: dict[str, Any] | Callable[[], dict[str, Any]],
    extra_system: str = "",
) -> tuple[dict[str, Any], str]:
    system = load_prompt(prompt_name) or f"You are the {agent_name} for Ventauri. Respond with JSON only."
    if extra_system.strip():
        system = f"{system}\n\n{extra_system.strip()}"
    settings = get_settings()
    if settings.llm_enabled:
        log_event(
            "agent.llm",
            "openai_chat_request",
            detail={
                "agent_name": agent_name,
                "prompt_name": prompt_name,
                "system_chars": len(system),
                "user_chars": len(user_message),
                "model": settings.openai_model,
            },
        )
        raw = await complete_chat(system, user_message)
        log_event(
            "agent.llm",
            "openai_chat_response",
            detail={
                "agent_name": agent_name,
                "assistant_chars": len(raw or ""),
            },
        )
        try:
            return parse_json_block(raw), raw
        except json.JSONDecodeError:
            log_event(
                "agent.llm",
                "json_parse_failed",
                level="warning",
                detail={"agent_name": agent_name, "raw_chars": len(raw or "")},
            )
            return {"parse_error": True, "raw": raw}, raw
    log_event(
        "agent.llm",
        "demo_mode_structured_output",
        detail={"agent_name": agent_name, "prompt_name": prompt_name},
    )
    data = demo_factory() if callable(demo_factory) else demo_factory
    return data, json.dumps(data, indent=2)


def build_output(agent_name: str, data: dict[str, Any], raw: str) -> AgentOutput:
    summary = (
        data.get("summary")
        or data.get("executive_summary")
        or data.get("recommended_focus")
        or data.get("market_notes")
        or data.get("compliance_posture")
        or ""
    )
    if isinstance(summary, list):
        summary = "; ".join(str(x) for x in summary[:3])
    summary = str(summary)[:500]
    return AgentOutput(
        agent_name=agent_name,
        summary=summary or f"{agent_name} completed",
        structured=data,
        raw_text=raw,
    )
