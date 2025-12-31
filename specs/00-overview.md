# Overview — Hackathon 1 Unified Book + RAG Chatbot

## Goal
Publish a Docusaurus book on GitHub Pages and embed a RAG chatbot that answers questions using only `/book/docs`, including a “selected text only” answering mode.

## Constraints
- Spec-driven development: implement only what is specified.
- TDD: tests first.
- Python 3.12+, uv, pytest.
- Minimum 80% coverage.
- Use dataclasses for core data structures (where appropriate).
- Keep all project files in git.
- Backend deploy target: Render.
- DB: Neon Serverless Postgres; Vector DB: Qdrant Cloud free tier.

## Milestones
M1 Monorepo + book live (already done)
M2 Backend skeleton (health/ready) + CI tests
M3 Database schema + Qdrant collections
M4 Ingestion CLI: docs → chunks → embeddings → Qdrant + Neon
M5 RAG chat endpoints (book-only) + citations
M6 Selected-text-only mode endpoint
M7 Frontend chat widget + selection UI embedded in Docusaurus
M8 Render deployment + production config

## Definition of Done (global)
- Specs satisfied
- Tests pass
- ≥ 80% coverage
- ADRs added for important decisions
- Deployed book + deployed backend work end-to-end
