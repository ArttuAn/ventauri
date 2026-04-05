from __future__ import annotations

from collections.abc import Callable
from typing import Any

from memory.vector_store import VectorRecord, VectorStore


class AgentMemory:
    """
    Per-agent, per-session view over the shared VectorStore.
    Writes and recalls are tagged so agents do not bleed context across agents or sessions.
    """

    def __init__(self, agent_id: str, session_id: str, vectors: VectorStore) -> None:
        self.agent_id = agent_id
        self.session_id = session_id
        self._vectors = vectors

    def _match(self) -> Callable[[VectorRecord], bool]:
        aid, sid = self.agent_id, self.session_id

        def _m(rec: VectorRecord) -> bool:
            md = rec.metadata or {}
            return md.get("agent_id") == aid and md.get("session_id") == sid

        return _m

    def remember(self, key: str, text: str, extra_metadata: dict[str, Any] | None = None) -> None:
        meta: dict[str, Any] = {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
        }
        if extra_metadata:
            meta.update(extra_metadata)
        doc_id = f"{self.session_id}:{self.agent_id}:{key}"
        self._vectors.add(doc_id, text, meta)

    def recall(self, query: str, k: int = 5) -> list[tuple[float, str, dict[str, Any]]]:
        hits = self._vectors.search_filtered(query, k=k * 3, match=self._match())
        out: list[tuple[float, str, dict[str, Any]]] = []
        for score, rec in hits:
            out.append((score, rec.text, dict(rec.metadata or {})))
            if len(out) >= k:
                break
        return out

    def recall_snippets(self, query: str, k: int = 5, max_chars: int = 1200) -> str:
        parts: list[str] = []
        n = 0
        for _s, text, _md in self.recall(query, k=k):
            parts.append(text)
            n += len(text)
            if n >= max_chars:
                break
        return "\n---\n".join(parts) if parts else "(no prior memory for this agent in this session)"
