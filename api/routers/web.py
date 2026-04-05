from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from agents.registry import AGENTS
from api.database import async_session_maker, get_db
from api.jobs_store import create_job, get_job, update_job
from api.paths import TEMPLATES_DIR
from api.repo import count_reports, count_sessions, delete_session, get_session_by_id, list_recent_sessions
from api.schemas import RunAsyncAccepted, RunRequest, RunResponse
from api.run_service import run_venture_workflow
from memory.session_store import SessionStore
from orchestrator.runner import PIPELINE_STAGE_IDS, PipelineRunner
from orchestrator.telemetry import get_events, log_event

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _runner(request: Request) -> PipelineRunner:
    return request.app.state.runner


def _memory_sessions(request: Request) -> SessionStore:
    return request.app.state.memory_sessions


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    n_sess = await count_sessions(db)
    n_rep = await count_reports(db)
    recent = await list_recent_sessions(db, limit=8)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "session_count": n_sess,
            "report_count": n_rep,
            "recent": recent,
            "pipelines": PIPELINE_STAGE_IDS,
        },
    )


@router.get("/dashboard/agents", response_class=HTMLResponse)
async def dashboard_agents(request: Request) -> Any:
    return templates.TemplateResponse(
        request,
        "agents.html",
        {
            "request": request,
            "title": "Agents",
            "agents": AGENTS,
            "pipelines": PIPELINE_STAGE_IDS,
        },
    )


@router.get("/dashboard/run", response_class=HTMLResponse)
async def dashboard_run_get(request: Request) -> Any:
    return templates.TemplateResponse(
        request,
        "run.html",
        {
            "request": request,
            "title": "Run workflow",
            "pipelines": PIPELINE_STAGE_IDS,
        },
    )


@router.get("/dashboard/sessions", response_class=HTMLResponse)
async def dashboard_sessions(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    rows = await list_recent_sessions(db, limit=100)
    return templates.TemplateResponse(
        request,
        "sessions.html",
        {
            "request": request,
            "title": "Sessions & reports",
            "sessions": rows,
        },
    )


@router.get("/dashboard/sessions/{session_id}", response_class=HTMLResponse)
async def dashboard_session_detail(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    row = await get_session_by_id(db, session_id)
    if row is None:
        return templates.TemplateResponse(
            request,
            "not_found.html",
            {
                "request": request,
                "title": "Not found",
                "message": "That workflow session does not exist.",
            },
            status_code=404,
        )
    return templates.TemplateResponse(
        request,
        "session_detail.html",
        {
            "request": request,
            "title": f"Session {session_id[:8]}…",
            "session": row,
        },
    )


@router.post("/dashboard/sessions/{session_id}/delete")
async def dashboard_session_delete(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    await delete_session(db, session_id)
    return RedirectResponse(url="/dashboard/sessions", status_code=303)


@router.post("/api/run", response_model=RunResponse)
async def api_run(
    req: RunRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RunResponse:
    payload = await run_venture_workflow(
        goal=req.goal,
        pipeline=req.pipeline,
        runner=_runner(request),
        memory_sessions=_memory_sessions(request),
        db=db,
    )
    return RunResponse(**payload)


@router.get("/api/activity")
async def api_activity(
    since_id: int = 0,
    limit: int = 400,
    job_id: str | None = None,
) -> dict[str, Any]:
    return {"events": get_events(since_id=since_id, limit=limit, job_id=job_id)}


@router.get("/api/jobs/{job_id}")
async def api_job_status(job_id: str) -> dict[str, Any]:
    row = get_job(job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")
    return {"job_id": job_id, **row}


@router.post("/api/run/async", response_model=RunAsyncAccepted)
async def api_run_async(req: RunRequest, request: Request) -> RunAsyncAccepted:
    job_id = create_job()
    runner = _runner(request)
    mem = _memory_sessions(request)
    log_event(
        "api",
        "run_async_accepted",
        detail={"job_id": job_id, "goal_chars": len(req.goal), "pipeline": req.pipeline},
    )

    async def work() -> None:
        update_job(job_id, status="running")
        log_event("job", "worker_started", detail={"job_id": job_id})
        try:
            async with async_session_maker() as db:
                payload = await run_venture_workflow(
                    goal=req.goal,
                    pipeline=req.pipeline,
                    runner=runner,
                    memory_sessions=mem,
                    db=db,
                    job_id=job_id,
                )
                await db.commit()
            update_job(
                job_id,
                status="completed",
                session_id=payload["session_id"],
                pipeline_id=payload["pipeline_id"],
                route_reason=payload["route_reason"],
            )
            log_event(
                "job",
                "worker_finished",
                detail={"job_id": job_id, "session_id": payload["session_id"]},
            )
        except Exception as e:
            update_job(job_id, status="failed", error=str(e))
            log_event(
                "job",
                "worker_failed",
                level="error",
                detail={"job_id": job_id, "exc_type": type(e).__name__, "error": str(e)[:2000]},
            )

    asyncio.create_task(work())
    return RunAsyncAccepted(job_id=job_id)
