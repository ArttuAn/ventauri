from __future__ import annotations

from typing import Any

from agents.registry import display_agent_title
from orchestrator.chat_router import route_chat_message
from orchestrator.models import WorkflowState
from orchestrator.runner import CHAT_AGENT_RUNNERS, PipelineRunner
from orchestrator.telemetry import log_event, telemetry_scope

RAW_TEXT_MAX = 48_000


async def run_routed_chat_turn(message: str, runner: PipelineRunner) -> dict[str, Any]:
    msg = message.strip()
    routing = await route_chat_message(msg)
    fn = CHAT_AGENT_RUNNERS.get(routing.selected_agent_id)
    if fn is None:
        raise RuntimeError(f"No runner registered for agent {routing.selected_agent_id!r}")

    state = WorkflowState(user_goal=msg)
    log_event(
        "chat",
        "agent_invoke",
        detail={"session_id": state.session_id, "agent": routing.selected_agent_id},
    )
    async with telemetry_scope(stage=routing.selected_agent_id):
        out = await fn(state, runner.sessions, runner.vectors, {})

    info = get_agent(routing.selected_agent_id)
    agent_title = info.title if info else routing.selected_agent_id.replace("_", " ").title()

    raw = out.raw_text or ""
    truncated = len(raw) > RAW_TEXT_MAX
    if truncated:
        raw = raw[:RAW_TEXT_MAX] + "\n… [truncated]"

    log_event(
        "chat",
        "agent_done",
        detail={
            "session_id": state.session_id,
            "agent": out.agent_name,
            "summary_chars": len(out.summary or ""),
        },
    )

    return {
        "session_id": state.session_id,
        "routing": {
            "selected_agent_id": routing.selected_agent_id,
            "agent_title": agent_title,
            "reasoning": routing.reasoning,
            "evidence": routing.evidence,
            "confidence": routing.confidence,
            "source": routing.source,
        },
        "agent_output": {
            "agent_name": out.agent_name,
            "agent_display_title": agent_title,
            "summary": out.summary,
            "structured": out.structured,
            "raw_text": raw,
            "raw_truncated": truncated,
            "citations": list(out.citations or []),
        },
    }
