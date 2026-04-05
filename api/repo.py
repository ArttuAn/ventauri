from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models_db import AgentReportRow, WorkflowSessionRow
from orchestrator.models import AgentOutput, WorkflowState


async def save_workflow_result(
    db: AsyncSession,
    state: WorkflowState,
    route_reason: str,
    outputs: list[AgentOutput],
    stages: list[str],
) -> None:
    history: list[dict[str, Any]] = [dict(e) for e in state.history]
    row = WorkflowSessionRow(
        id=state.session_id,
        user_goal=state.user_goal,
        pipeline_id=state.pipeline_id,
        route_reason=route_reason,
        status="completed",
        stage=state.stage,
        history_json=history,
    )
    db.add(row)
    for i, out in enumerate(outputs):
        stage = stages[i] if i < len(stages) else out.agent_name
        db.add(
            AgentReportRow(
                session_id=state.session_id,
                agent_name=out.agent_name,
                stage=stage,
                position=i,
                summary=out.summary,
                structured=dict(out.structured),
                raw_text=out.raw_text or "",
            )
        )
    await db.flush()


async def count_sessions(db: AsyncSession) -> int:
    r = await db.execute(select(func.count()).select_from(WorkflowSessionRow))
    return int(r.scalar_one())


async def count_reports(db: AsyncSession) -> int:
    r = await db.execute(select(func.count()).select_from(AgentReportRow))
    return int(r.scalar_one())


async def list_recent_sessions(db: AsyncSession, limit: int = 50) -> list[WorkflowSessionRow]:
    q = (
        select(WorkflowSessionRow)
        .options(selectinload(WorkflowSessionRow.reports))
        .order_by(WorkflowSessionRow.created_at.desc())
        .limit(limit)
    )
    r = await db.execute(q)
    return list(r.scalars().unique().all())


async def get_session_by_id(db: AsyncSession, session_id: str) -> WorkflowSessionRow | None:
    q = (
        select(WorkflowSessionRow)
        .where(WorkflowSessionRow.id == session_id)
        .options(selectinload(WorkflowSessionRow.reports))
    )
    r = await db.execute(q)
    row = r.scalar_one_or_none()
    if row is None:
        return None
    row.reports.sort(key=lambda x: x.position)
    return row


async def delete_session(db: AsyncSession, session_id: str) -> bool:
    from sqlalchemy import delete

    await db.execute(delete(AgentReportRow).where(AgentReportRow.session_id == session_id))
    res = await db.execute(delete(WorkflowSessionRow).where(WorkflowSessionRow.id == session_id))
    return (res.rowcount or 0) > 0
