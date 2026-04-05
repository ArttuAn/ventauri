from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np


def _cheap_embedding(text: str, dim: int = 96) -> np.ndarray:
    v = np.zeros(dim, dtype=np.float32)
    for token in text.lower().split():
        digest = hashlib.md5(token.encode(), usedforsecurity=False).hexdigest()
        h = int(digest[:8], 16) % dim
        v[h] += 1.0
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


@dataclass
class VectorRecord:
    id: str
    text: str
    metadata: dict[str, Any]
    vector: np.ndarray


class VectorStore:
    """Tiny in-process vector index (swap for FAISS / hosted vector DB)."""

    def __init__(self, dim: int = 96) -> None:
        self.dim = dim
        self._records: list[VectorRecord] = []

    def add(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        meta = metadata or {}
        vec = _cheap_embedding(text, self.dim)
        self._records.append(VectorRecord(id=doc_id, text=text, metadata=meta, vector=vec))

    def search(self, query: str, k: int = 5) -> list[tuple[float, VectorRecord]]:
        q = _cheap_embedding(query, self.dim)
        scored = [(_cosine(q, r.vector), r) for r in self._records]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]

    def search_filtered(
        self,
        query: str,
        k: int,
        match: Callable[[VectorRecord], bool],
    ) -> list[tuple[float, VectorRecord]]:
        q = _cheap_embedding(query, self.dim)
        scored = [(_cosine(q, r.vector), r) for r in self._records if match(r)]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]
