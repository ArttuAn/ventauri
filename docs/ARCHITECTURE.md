# Ventauri — Architecture

## Core concept

Specialized agents coordinated by an **orchestrator**, backed by:

- Shared memory (session + vectors + episodic logs)
- Tool integrations (**skills**)
- Task routing and workflow state
- Long/short-term planning loops (extensible)
- Feedback and learning hooks (future)

## Components

### 1. Orchestrator (agent router)

- Decides which agent(s) to invoke
- Breaks goals into tasks
- Maintains workflow state
- Handles retries and prioritization (hooks in code)

### 2. Specialized agents (MVP + expansion)

| Agent | Focus |
|--------|--------|
| Idea | Ideation, scoring, clustering |
| Research | Market, competitors, trends, personas |
| Validation | MVPs, experiments, signals |
| Strategy | Business model, GTM, SWOT |
| Product | Features, MVP scope, roadmap |
| Marketing | Content, SEO, social, copy |
| Finance | Projections, burn, unit economics |
| Growth | Funnels, A/B tests, retention |
| Ops | Hiring, processes, tool stack |

**MVP ships with Idea, Research, Strategy.** Other directories may contain stubs or READMEs until implemented.

### 3. Memory

1. **Short-term (session)** — active goals, recent turns, task context  
2. **Long-term (vector)** — preferences, past ideas, validated insights  
3. **Episodic** — decisions, experiments, outcomes (log interface)  
4. **Knowledge base** — frameworks, templates (`prompts/`, `configs/`)

### 4. Skills / tooling

Pluggable capabilities: `web_search`, scrapers, simulators, `vector_store_query`, `document_writer`, **brand naming** (`skills/branding_tools`, distinctiveness heuristics + candidate lists), etc. Implemented under `skills/` with clear interfaces.

### 5. Agent communication (options)

- Direct orchestrated tool-calling (current MVP)
- Shared message bus / task queue (future)
- Patterns: planner → executor, debate, critic loops, reflexion

## Workflows (examples)

1. **Idea → validation** — Idea → Research → Validation → Strategy (partially stubbed)  
2. **Idea → MVP plan** — Product + Ops (future)  
3. **Growth loop** — Marketing + Growth + metrics (future)

## Tech stack (suggested evolution)

- **Now**: Python, FastAPI, Typer, Pydantic, NumPy (vectors), optional OpenAI SDK  
- **Next**: LangGraph, Redis/Celery, Postgres, React/Next dashboard, hosted vector DB  

This document is the north star; the code in `main` tracks the **MVP** first, then expands.
