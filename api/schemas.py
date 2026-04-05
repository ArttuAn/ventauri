from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    pipeline: str | None = Field(
        default=None,
        description="Pipeline id, e.g. idea-to-strategy. Auto-routed when omitted.",
    )


class RunResponse(BaseModel):
    session_id: str
    pipeline_id: str
    route_reason: str
    outputs: list[dict[str, Any]]
