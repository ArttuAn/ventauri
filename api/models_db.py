from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class WorkflowSessionRow(Base):
    __tablename__ = "workflow_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_goal: Mapped[str] = mapped_column(Text)
    pipeline_id: Mapped[str] = mapped_column(String(64))
    route_reason: Mapped[str] = mapped_column(String(512), default="")
    status: Mapped[str] = mapped_column(String(32), default="completed")
    stage: Mapped[str] = mapped_column(String(64), default="completed")
    history_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    reports: Mapped[list["AgentReportRow"]] = relationship(
        back_populates="workflow_session",
        cascade="all, delete-orphan",
    )


class AgentReportRow(Base):
    __tablename__ = "agent_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflow_sessions.id", ondelete="CASCADE"))
    agent_name: Mapped[str] = mapped_column(String(64))
    stage: Mapped[str] = mapped_column(String(64))
    position: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, default="")
    structured: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workflow_session: Mapped["WorkflowSessionRow"] = relationship(back_populates="reports")
