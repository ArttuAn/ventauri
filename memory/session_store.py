from __future__ import annotations

from orchestrator.models import WorkflowState


class SessionStore:
    """In-memory session backing store (swap for Redis/Postgres)."""

    def __init__(self) -> None:
        self._by_id: dict[str, WorkflowState] = {}

    def save(self, state: WorkflowState) -> None:
        self._by_id[state.session_id] = state

    def get(self, session_id: str) -> WorkflowState | None:
        return self._by_id.get(session_id)

    def delete(self, session_id: str) -> None:
        self._by_id.pop(session_id, None)
