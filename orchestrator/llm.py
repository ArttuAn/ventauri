from __future__ import annotations

import json
import re
from typing import Any

import httpx

from orchestrator.settings import get_settings


async def complete_chat(system: str, user: str) -> str:
    """Return assistant text; uses OpenAI-compatible chat API if configured, else demo stub."""
    settings = get_settings()
    if not settings.llm_enabled:
        return _demo_response(system, user)

    url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


def _demo_response(system: str, user: str) -> str:
    """Deterministic placeholder when no API key is set."""
    goal = user.strip() or "your venture"
    return json.dumps(
        {
            "mode": "demo",
            "note": "Set OPENAI_API_KEY for live LLM output.",
            "user_goal_echo": goal,
            "system_hint": system[:200] + ("…" if len(system) > 200 else ""),
        },
        indent=2,
    )


def parse_json_block(text: str) -> dict[str, Any]:
    """Extract JSON object from model output (handles fenced blocks)."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)
