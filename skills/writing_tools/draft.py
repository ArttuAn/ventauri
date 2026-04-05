from __future__ import annotations


def draft_outline(title: str, bullets: list[str]) -> str:
    """Lightweight outline helper — extend with LLM-backed copy."""
    body = "\n".join(f"- {b}" for b in bullets)
    return f"# {title}\n\n{body}\n"
