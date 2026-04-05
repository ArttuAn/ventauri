# FounderOS

**Multi-Agent AI Operating System for Entrepreneurs** — a modular framework of AI agents that collaborate from idea discovery → validation → launch → growth.

This repository is a **framework and reference implementation**, not a single chatbot: shared memory, pluggable skills, orchestration, and workflows you can extend.

## MVP (this release)

- **Orchestrator**: routes goals, runs staged workflows, keeps session state
- **Agents**: **Idea**, **Research**, **Strategy** (more agent slots are reserved in the tree for expansion)
- **Memory**: session store + lightweight semantic vector store (embeddings optional via OpenAI)
- **Interfaces**: **CLI** (`founderos`) and minimal **FastAPI** service

## Architecture (high level)

| Layer | Role |
|--------|------|
| **Orchestrator** | Task breakdown, agent selection, retries, workflow state |
| **Agents** | Specialized prompts + structured outputs + skill hooks |
| **Memory** | Short-term session, long-term vectors, episodic log hooks |
| **Skills** | Reusable tools (web, writing, analytics stubs; extend with real APIs) |

See `docs/ARCHITECTURE.md` for the full conceptual map (agents, memory types, communication patterns).

## Quick start

```bash
cd founderOS  # or founderOS on Windows
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -e ".[openai]"   # optional: real LLM calls
pip install -e .

# CLI
founderos --help
founderos run "I want a B2B SaaS for small clinics" --pipeline idea-to-strategy

# API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment

Copy `.env.example` to `.env`. Without `OPENAI_API_KEY`, agents run in **deterministic demo mode** (structured placeholders) so the repo runs offline.

## Repository layout

```
orchestrator/     # Router, state, pipeline runner
agents/           # idea_agent, research_agent, strategy_agent (+ stubs for future agents)
memory/           # session_store, vector_store, episodic hooks
skills/           # web_tools, data_tools, writing_tools, analytics_tools
workflows/        # Declarative stage graphs
prompts/          # Agent system / task prompts
configs/          # YAML defaults
api/              # FastAPI app
cli/              # Typer CLI
```

## Roadmap

- Additional agents (validation, product, marketing, finance, growth, ops)
- LangGraph-style graphs, Redis queue, Postgres persistence
- Founder dashboard (Next.js), experiment tracker, debate/critic loops

## License

MIT
