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


class RunAsyncAccepted(BaseModel):
    job_id: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=12_000)


class ChatRoutingBlock(BaseModel):
    selected_agent_id: str
    agent_title: str
    reasoning: str
    evidence: list[str]
    confidence: float
    source: str = Field(
        description="How routing was chosen: model | keywords | model_fallback",
    )


class ChatAgentOutputBlock(BaseModel):
    agent_name: str
    agent_display_title: str = Field(
        description="Registry display name, e.g. Compliance Agent",
    )
    summary: str
    structured: dict[str, Any]
    raw_text: str = ""
    raw_truncated: bool = False
    citations: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    session_id: str
    routing: ChatRoutingBlock
    agent_output: ChatAgentOutputBlock
