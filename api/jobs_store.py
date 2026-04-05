from __future__ import annotations

import threading
import uuid
from typing import Any


_jobs: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


def create_job() -> str:
    jid = str(uuid.uuid4())
    with _lock:
        _jobs[jid] = {
            "status": "queued",
            "session_id": None,
            "pipeline_id": None,
            "route_reason": None,
            "error": None,
        }
    return jid


def update_job(job_id: str, **kwargs: Any) -> None:
    with _lock:
        if job_id not in _jobs:
            return
        _jobs[job_id].update(kwargs)


def get_job(job_id: str) -> dict[str, Any] | None:
    with _lock:
        j = _jobs.get(job_id)
        return dict(j) if j else None
