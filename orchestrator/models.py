from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AgentOutput(BaseModel):
    agent_name: str
    summary: str
    structured: dict[str, Any] = Field(default_factory=dict)
    raw_text: str = ""
    citations: list[str] = Field(default_factory=list)


class WorkflowState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_goal: str = ""
    pipeline_id: str = ""
    stage: str = "init"
    history: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    def touch(self) -> None:
        self.updated_at = _utc_now()

    def append_event(self, kind: str, payload: dict[str, Any]) -> None:
        self.history.append({"kind": kind, "at": _utc_now().isoformat(), **payload})
        self.touch()
