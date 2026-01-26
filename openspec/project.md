# Project Context

## Purpose
Minimal Python library for forwarding LLM-style prompts to a user-supplied HTTP backend. Provides a single primitive (`clx_query`) plus thin helpers and SQL adapters so Python code and SQL engines can call the same backend without bundling model logic in the client.

## Tech Stack
- Python 3.8+ with standard library typing/dataclasses, sqlite3, argparse
- `requests` for HTTP calls to the backend; `tomllib` fallback for Python <3.11 config parsing
- Optional runtime deps owned by the user: `pyspark` or `duckdb` (only when using their adapters)
- Packaging via `setuptools` in `pyproject.toml`; published as `clx-cli`

## Project Conventions

### Code Style
- Favor standard library over new dependencies; keep modules small and readable
- Use type hints and straightforward control flow; minimal abstractions
- Keep public surface area tiny (primarily `clx_query` plus helper wrappers); explicit error messages
- Docstrings for modules/functions; avoid non-ASCII unless required

### Architecture Patterns
- Backend-agnostic resolver: all intelligence (routing, eval, auth) lives in the backend
- Core primitive: `clx_query(model, prompt, params, ...)` -> HTTP POST to backend, expecting `{"output": ...}` (or `response`)
- Config resolution order: explicit arg > `CLX_BACKEND_URL` env var > `~/.clx/config.toml`
- Optional caching: SQLite file (`~/.clx_cache.db`) keyed by backend URL/path + model/prompt/params/metadata
- Pod/actor routing: builds `/pods/{pod}/actors/{actor}/run` when `CLX_POD_NAME` and `CLX_ACTOR_ID` are set (or passed)
- Helpers are prompt templates only (summarize, classify, extract, etc.); adapters register `clx_query` as a SQL function for Spark, DuckDB, and SQLite

### Testing Strategy
- No automated test suite yet; rely on manual smoke tests against a real backend
- Typical checks: run `demo_backend_call.py` with env vars set, plus simple `clx_query`/adapter calls to confirm HTTP contract and JSON handling
- Keep changes small; avoid introducing heavyweight test frameworks without need

### Git Workflow
- No repo-specific workflow documented; use small feature branches and concise commits
- Follow OpenSpec guidance: create proposals for new capabilities or architectural changes before implementation
- Avoid rewriting shared history; prefer reviewable, minimal diffs

## Domain Context
- Client-only AI resolver; never calls OpenAI/Ollama/Databricks directly—everything is forwarded to a user-provided backend implementing `/v1/query` (or pod/actor route)
- Backend response must include `output` (or `response`); `expect_json=True` enforces JSON parsing
- Designed to stay tiny and backend-agnostic while supporting SQL engines via UDF registration

## Important Constraints
- Maintain minimal dependency footprint and Python 3.8+ compatibility
- Preserve backend-agnostic design; do not bake provider-specific logic into the client
- Keep contract stability: HTTP POST with model/prompt/params/metadata and `output`/`response` field expected
- Local caching is optional and must remain opt-in; defaults should not create files unless cache is used

## External Dependencies
- User-supplied HTTP backend at `/v1/query` or `/pods/{pod}/actors/{actor}/run`
- Local SQLite file for caching (`~/.clx_cache.db`) when enabled
- Optional ecosystems: Spark (pyspark) and DuckDB for SQL adapters; SQLite built-in
