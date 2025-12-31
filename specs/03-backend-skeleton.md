# Feature: Backend Skeleton (FastAPI + uv)

## Requirements
- Backend path: `/backend`.
- Use uv for dependency management.
- FastAPI app exposes:
  - GET `/health` → {"status":"ok"}
  - GET `/ready` → checks connectivity to Neon + Qdrant (returns ok or clear error)
- Config via environment variables validated at startup.
- CORS allows GitHub Pages origin (origin only, no path).

## Acceptance Criteria
- `uv run pytest` passes.
- `uv run uvicorn app.main:app --reload` starts locally.
- `/health` returns 200 always.
- `/ready` returns 200 only when external dependencies are configured and reachable.
