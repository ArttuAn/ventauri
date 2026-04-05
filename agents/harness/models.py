from __future__ import annotations

from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    recall_top_k: int = 4


class SkillBinding(BaseModel):
    name: str
    callable: str = Field(..., description="Dotted path: package.module.function_name")


class HarnessSpec(BaseModel):
    agent_id: str
    display_title: str = ""
    prompt_name: str
    rules_file: str = "rules.md"
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    skill_bindings: list[SkillBinding] = Field(default_factory=list)
    harness_instructions: str = ""
