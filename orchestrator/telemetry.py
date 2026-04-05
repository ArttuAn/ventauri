from __future__ import annotations

import itertools
import threading
from collections import deque
from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

_MAX = 2000
_buffer: deque[dict[str, Any]] = deque(maxlen=_MAX)
_lock = threading.Lock()
_id_gen = itertools.count(1)

_trace: ContextVar[dict[str, str]] = ContextVar("ventauri_telemetry_trace", default={})


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def current_trace() -> dict[str, str]:
    return dict(_trace.get())


@asynccontextmanager
async def telemetry_scope(
    *,
    job_id: str | None = None,
    session_id: str | None = None,
    pipeline_id: str | None = None,
    stage: str | None = None,
):
    prev = _trace.get()
    new = {**prev}
    if job_id is not None:
        new["job_id"] = job_id
    if session_id is not None:
        new["session_id"] = session_id
    if pipeline_id is not None:
        new["pipeline_id"] = pipeline_id
    if stage is not None:
        new["stage"] = stage
    token = _trace.set(new)
    try:
        yield
    finally:
        _trace.reset(token)


def log_event(
    source: str,
    message: str,
    *,
    level: str = "info",
    detail: dict[str, Any] | None = None,
) -> int:
    """Append one technical event; returns monotonic event id (thread-safe)."""
    trace = current_trace()
    row: dict[str, Any] = {
        "id": next(_id_gen),
        "ts": _utc_iso(),
        "source": source,
        "message": message,
        "level": level,
        "detail": detail if detail is not None else {},
    }
    row.update(trace)
    with _lock:
        _buffer.append(row)
    return int(row["id"])


def get_events(
    *,
    since_id: int = 0,
    limit: int = 200,
    job_id: str | None = None,
) -> list[dict[str, Any]]:
    """Events with id > since_id, optional job_id filter, chronological order, at most `limit` rows."""
    with _lock:
        items = list(_buffer)
    matching: list[dict[str, Any]] = []
    for e in items:
        if e["id"] <= since_id:
            continue
        if job_id is not None and e.get("job_id") != job_id:
            continue
        matching.append(dict(e))
    return matching[-limit:]


def snapshot_tail(limit: int = 100) -> list[dict[str, Any]]:
    with _lock:
        items = list(_buffer)[-limit:]
    return [dict(e) for e in items]
