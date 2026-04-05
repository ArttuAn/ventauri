from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def prompts_dir() -> Path:
    return _REPO_ROOT / "prompts"


@lru_cache
def load_prompt(name: str) -> str:
    path = prompts_dir() / f"{name}.md"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")
