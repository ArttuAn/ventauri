from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agents.base import build_output, run_json_agent
from agents.harness.loader import load_harness_spec
from agents.harness.skills_exec import resolve_callable, run_skill
from memory.agent_memory import AgentMemory
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import AgentOutput, WorkflowState

UserMessageFn = Callable[[dict[str, Any]], str]
DemoFactory = dict[str, Any] | Callable[[], dict[str, Any]]


async def run_harnessed_turn(
    *,
    harness_dir: Path,
    state: WorkflowState,
    _sessions: SessionStore,
    vectors: VectorStore,
    prior: dict[str, Any],
    demo_factory: DemoFactory,
    user_message_fn: UserMessageFn,
    vector_doc_suffix: str,
) -> AgentOutput:
    spec = load_harness_spec(harness_dir / "harness.yaml")
    rules_path = harness_dir / spec.rules_file
    rules_text = rules_path.read_text(encoding="utf-8") if rules_path.is_file() else ""

    ctx_base = {"session_id": state.session_id, "agent_id": spec.agent_id}
    skill_outputs: dict[str, Any] = {}
    for binding in spec.skill_bindings:
        fn = resolve_callable(binding.callable)
        skill_outputs[binding.name] = run_skill(
            fn,
            goal=state.user_goal,
            prior=prior,
            context=dict(ctx_base),
        )

    memory = AgentMemory(spec.agent_id, state.session_id, vectors)
    recall_txt = memory.recall_snippets(state.user_goal, k=spec.memory.recall_top_k)

    user_ctx: dict[str, Any] = {
        "goal": state.user_goal,
        "prior": prior,
        "skills": skill_outputs,
        "memory_recall": recall_txt,
        "agent_id": spec.agent_id,
    }
    user_message = user_message_fn(user_ctx)

    extra_parts = [
        "--- RULES (binding) ---",
        rules_text,
    ]
    if spec.harness_instructions.strip():
        extra_parts.extend(["--- HARNESS INSTRUCTIONS ---", spec.harness_instructions.strip()])
    extra_parts.extend(
        [
            "--- SKILL OUTPUT (ground with this; stubs until real integrations) ---",
            json.dumps(skill_outputs, indent=2, ensure_ascii=False)[:12000],
            "--- MEMORY RECALL (this agent + session only) ---",
            recall_txt,
        ]
    )
    extra_system = "\n".join(extra_parts)

    data, raw = await run_json_agent(
        agent_name=spec.agent_id,
        prompt_name=spec.prompt_name,
        user_message=user_message,
        demo_factory=demo_factory,
        extra_system=extra_system,
    )

    memory.remember(
        "latest_report",
        json.dumps(data, ensure_ascii=False)[:6000],
        {"kind": "report_snapshot"},
    )

    out = build_output(spec.agent_id, data, raw)
    vectors.add(
        f"{state.session_id}:{vector_doc_suffix}",
        json.dumps(data, ensure_ascii=False),
        {"agent_id": spec.agent_id, "session_id": state.session_id, "kind": "agent_report"},
    )
    return out
