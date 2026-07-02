from __future__ import annotations

import asyncio
import json
from typing import Optional

import typer

from api.database import async_session_maker, init_db
from api.run_service import resolve_pipeline, run_venture_workflow
from memory.session_store import SessionStore
from memory.vector_store import VectorStore
from orchestrator.models import WorkflowState
from orchestrator.runner import PIPELINE_STAGE_IDS, PipelineRunner
from skills.branding_tools.naming import generate_name_candidates

app = typer.Typer(no_args_is_help=True, help="Ventauri — multi-agent founder workflows")


@app.command("run")
def run_cmd(
    goal: str = typer.Argument(..., help="What the founder wants to achieve"),
    pipeline: Optional[str] = typer.Option(
        None,
        "--pipeline",
        "-p",
        help="Pipeline id (default: auto-route)",
    ),
    json_out: bool = typer.Option(False, "--json", help="Print machine-readable JSON"),
    persist: bool = typer.Option(
        True,
        "--persist/--no-persist",
        help="Save workflow + reports to data/ventauri.db (default: persist)",
    ),
) -> None:
    """Run a pipeline and optionally persist results to SQLite."""

    async def _run() -> None:
        sessions = SessionStore()
        vectors = VectorStore()
        runner = PipelineRunner(sessions, vectors)

        try:
            resolve_pipeline(goal, pipeline)
        except ValueError as e:
            typer.secho(str(e), fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1) from e

        if persist:
            await init_db()
            async with async_session_maker() as db:
                payload = await run_venture_workflow(
                    goal=goal,
                    pipeline=pipeline,
                    runner=runner,
                    memory_sessions=sessions,
                    db=db,
                )
                await db.commit()
        else:
            pipeline_id, reason = resolve_pipeline(goal, pipeline)
            state = WorkflowState(user_goal=goal)
            outputs = await runner.run_pipeline(state, pipeline_id)
            payload = {
                "session_id": state.session_id,
                "pipeline_id": pipeline_id,
                "route_reason": reason,
                "outputs": [
                    {
                        "agent": o.agent_name,
                        "summary": o.summary,
                        "structured": o.structured,
                    }
                    for o in outputs
                ],
            }

        if json_out:
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
            return

        typer.echo(f"Session: {payload['session_id']}")
        typer.echo(f"Pipeline: {payload['pipeline_id']} ({payload['route_reason']})")
        if persist:
            typer.echo("Saved to data/ventauri.db — view in dashboard → Sessions")
        else:
            typer.echo("(not persisted — use default --persist or the web dashboard)")
        typer.echo("")
        for o in payload["outputs"]:
            typer.echo(f"## {o['agent'].upper()}")
            typer.echo(o["summary"])
            typer.echo("")

    asyncio.run(_run())


@app.command("pipelines")
def pipelines_cmd() -> None:
    """List registered pipelines and stages."""
    for pid, stages in PIPELINE_STAGE_IDS.items():
        typer.echo(f"{pid}: {', '.join(stages)}")


@app.command("names")
def names_cmd(
    seed: str = typer.Argument(..., help="Vision, product type, or keywords to inspire names"),
    count: int = typer.Option(12, "--count", "-n", help="How many candidates"),
    json_out: bool = typer.Option(False, "--json", help="Print machine-readable JSON"),
) -> None:
    """Suggest distinctive name candidates (verify GitHub/npm/domain yourself)."""
    rows = generate_name_candidates(seed, count=count)
    if json_out:
        typer.echo(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    for row in rows:
        typer.echo(f"{row['name']}  (slug: {row['slug']}, score: {row['distinctiveness']})")
        typer.echo(f"  {row['rationale']}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
