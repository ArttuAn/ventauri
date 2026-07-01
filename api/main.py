from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import async_session_maker, get_db, init_db
from api.paths import STATIC_DIR
from api.routers import web as web_router
from api.chat_service import run_routed_chat_turn
from api.schemas import ChatRequest, ChatResponse, RunRequest, RunResponse
from api.run_service import run_venture_workflow
from orchestrator.telemetry import log_event
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.runner import PIPELINE_STAGE_IDS, PipelineRunner
from orchestrator.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    app.state.memory_sessions = SessionStore()
    app.state.vectors = VectorStore()
    app.state.runner = PipelineRunner(app.state.memory_sessions, app.state.vectors)
    yield


app = FastAPI(
    title="Ventauri API",
    version="0.1.0",
    description="Multi-agent orchestration for founder workflows (Ventauri)",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(web_router.router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=307)


@app.get("/health")
async def health() -> dict[str, str]:
    db_status = "error"
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            db_status = "ok"
    except Exception:
        pass
    settings = get_settings()
    overall = "ok" if db_status == "ok" else "degraded"
    return {
        "status": overall,
        "version": app.version,
        "db": db_status,
        "llm": "enabled" if settings.llm_enabled else "demo",
    }


@app.get("/pipelines")
def pipelines() -> dict[str, list[str]]:
    return PIPELINE_STAGE_IDS


@app.post("/api/chat", response_model=ChatResponse, name="ventauri_api_chat")
async def api_chat(req: ChatRequest, request: Request) -> ChatResponse:
    try:
        payload = await run_routed_chat_turn(req.message, request.app.state.runner)
        return ChatResponse(**payload)
    except Exception as e:
        log_event(
            "api",
            "chat_failed",
            level="error",
            detail={"exc_type": type(e).__name__, "error": str(e)[:2000]},
        )
        raise HTTPException(status_code=500, detail="Chat turn failed. Check logs / activity.") from e


@app.post("/run", response_model=RunResponse)
async def run_pipeline_json(
    req: RunRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RunResponse:
    try:
        payload = await run_venture_workflow(
            goal=req.goal,
            pipeline=req.pipeline,
            runner=request.app.state.runner,
            memory_sessions=request.app.state.memory_sessions,
            db=db,
        )
        return RunResponse(**payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
