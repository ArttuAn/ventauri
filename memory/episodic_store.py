from __future__ import annotations

from typing import Any


class EpisodicStore:
    """Append-only decision / experiment log (MVP: process-local)."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def append(self, event: dict[str, Any]) -> None:
        self._events.append(event)

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._events[-limit:]
