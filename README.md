# Ventauri

**Repository:** [github.com/ArttuAn/ventauri](https://github.com/ArttuAn/ventauri)

**Multi-agent AI operating system for entrepreneurs** — a modular framework of AI agents that collaborate from idea discovery → validation → launch → growth.

This repository is a **framework and reference implementation**, not a single chatbot: shared memory, pluggable skills, orchestration, and workflows you can extend.

## MVP (this release)

- **Orchestrator**: routes goals, runs staged workflows, keeps session state
- **Agents**: **Venture intelligence** harnessed agents (**Compliance Agent**, **Market Research Agent**, **Competitor Analysis Agent**, **Product Development Agent**) plus **Idea → Research → Strategy** pipeline; more slots stubbed in-repo
- **Memory**: session store + lightweight semantic vector store (embeddings optional via OpenAI)
- **Interfaces**: **Web dashboard** (Jinja2 + local UI), **CLI** (`ventauri`), **FastAPI** + OpenAPI
- **Storage**: **SQLite** at `data/ventauri.db` (workflow runs, per-agent reports, workflow event log) — **web/API runs persist**; CLI runs are in-memory unless you use the API
- **Founder chat**: dashboard message box → routing agent picks one specialist → evidence, reasoning, and answer on the same page
- **Theme**: dark / light toggle (saved in `localStorage`)
- **Naming skill**: `skills/branding_tools` generates candidate product/repo names (heuristic distinctiveness + next-step checks); exposed on the CLI as `ventauri names`

## Architecture (high level)

| Layer | Role |
|--------|------|
| **Orchestrator** | Task breakdown, agent selection, retries, workflow state |
| **Agents** | Specialized prompts + structured outputs + skill hooks |
| **Memory** | Short-term session, long-term vectors, episodic log hooks |
| **Skills** | Reusable tools (web, writing, analytics, **branding/naming**, …) |

See `docs/ARCHITECTURE.md` for the full conceptual map (agents, memory types, communication patterns).

## Quick start

```bash
cd ventauri   # your clone folder may differ
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -e ".[dev,openai]"   # dev: pytest; openai: real LLM calls
pip install -e .

# CLI (does not write to SQLite — use dashboard or API for persisted runs)
ventauri --help
ventauri run "I want a B2B SaaS for small clinics" --pipeline idea-to-strategy
ventauri run "HIPAA-compliant CRM: competitors and MVP" --pipeline venture-intelligence
ventauri names "AI copilot for indie hackers" --count 8

# Web dashboard + API (same server)
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
# Then open http://127.0.0.1:8000/dashboard
```

### Environment

Copy `.env.example` to `.env`. Without `OPENAI_API_KEY`, agents run in **deterministic demo mode** (structured placeholders) so the repo runs offline. The chat router uses **keyword signals** offline; with an API key it can use the **model router**.

## HTTP API (summary)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness + SQLite ping + LLM mode (`demo` / `enabled`) |
| `GET` | `/pipelines` | Registered pipeline → stage ids |
| `POST` | `/run` | Run workflow (sync), persist to SQLite |
| `POST` | `/api/run` | Same as `/run` (dashboard) |
| `POST` | `/api/run/async` | Background job; poll `GET /api/jobs/{id}` |
| `POST` | `/api/chat` | Founder chat: route → one agent → structured answer |
| `GET` | `/api/activity` | Technical telemetry ring buffer (dashboard log) |
| `GET` | `/dashboard` | Web UI |

Full schema: `http://127.0.0.1:8000/docs`

## Repository layout

```
orchestrator/     # Router, chat router, state, pipeline runner
agents/           # Harnessed venture agents + idea/research/strategy (+ stubs)
memory/           # session_store, vector_store, episodic hooks
skills/           # web_tools, data_tools, writing_tools, analytics_tools, branding_tools
workflows/        # Declarative stage graphs
prompts/          # Agent system / task prompts
configs/          # YAML defaults
api/              # FastAPI app, DB layer, dashboard routes
templates/        # Jinja2 dashboard pages
static/           # Dashboard CSS
data/             # Local SQLite (gitignored except .gitkeep)
cli/              # Typer CLI
tests/            # pytest suite
```

## Roadmap

- Additional agents (validation, marketing, finance, growth, ops) — stubs in-repo
- LangGraph-style graphs, Redis queue, Postgres persistence
- Experiment tracker, debate/critic loops, episodic memory wiring

## License

MIT
