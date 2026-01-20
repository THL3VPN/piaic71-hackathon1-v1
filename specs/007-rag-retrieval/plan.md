# Implementation Plan: RAG Retrieval (Book-only)

**Branch**: `007-rag-retrieval` | **Date**: 2026-01-06 | **Spec**: [RAG Retrieval Spec](spec.md)
**Input**: Feature specification from `/specs/007-rag-retrieval/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a RAG (Retrieval-Augmented Generation) system that allows users to query book content from `/book/docs` directory. The system performs question embedding, vector similarity search in Qdrant, retrieves relevant chunks from Neon database with citations, and builds contextual responses while preventing hallucination. The implementation includes configurable retrieval parameters, proper citation formatting, and graceful handling of low-confidence or empty retrieval results.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI (web framework), Qdrant client (vector database), SQLAlchemy (database ORM), OpenAI/Anthropic API (LLM), Sentence Transformers (embedding models), uv (dependency management)
**Storage**: PostgreSQL via Neon (document chunks with metadata), Qdrant (vector embeddings for similarity search)
**Testing**: pytest with unit, integration, and end-to-end tests
**Target Platform**: Linux server (backend service)
**Project Type**: web - backend service with RAG capabilities
**Performance Goals**: Process queries within 2 seconds, handle up to 10 retrieved chunks efficiently, maintain 99% uptime
**Constraints**: <200ms vector search latency, <100MB memory usage during context building, prevent hallucination at 100% rate
**Scale/Scope**: Handle 100+ concurrent users, process 10k+ document chunks, support multiple simultaneous queries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Spec-Driven Development: Following SDD methodology with clear spec, plan, and tasks
- ✅ PHR Compliance: All user inputs will be recorded in Prompt History Records
- ✅ ADR Documentation: Major architectural decisions will be documented if needed
- ✅ Authoritative Source: Using MCP tools and CLI commands for verification
- ✅ Test-First Approach: Tests will be written for all functionality
- ✅ Human-Centric Decision Making: Consulting user for clarifications when needed

## Project Structure

### Documentation (this feature)

```text
specs/007-rag-retrieval/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── rag.py                 # RAG endpoints and query processing
│   │   └── models.py              # Request/response models for RAG
│   ├── services/
│   │   ├── rag_service.py         # Core RAG orchestration logic
│   │   ├── embedding_service.py   # Question and document embedding
│   │   ├── retrieval_service.py   # Vector search and chunk retrieval
│   │   ├── qdrant_service.py      # Already exists, will be extended
│   │   └── citation_service.py    # Citation formatting and generation
│   ├── models/
│   │   ├── query.py               # Query input model
│   │   ├── retrieval_result.py    # Retrieval result model
│   │   └── context_bundle.py      # Context bundle with citations
│   ├── database/
│   │   ├── chunk_repository.py    # Already exists, may need extension
│   │   └── retrieval_repository.py # New - for retrieval statistics
│   └── utils/
│       ├── context_builder.py     # Build context from retrieved chunks
│       └── hallucination_guard.py  # Prevent hallucination logic
└── tests/
    ├── test_rag.py                # End-to-end RAG tests
    ├── test_retrieval.py          # Retrieval logic tests
    ├── test_citations.py          # Citation formatting tests
    └── test_hallucination_guard.py # Hallucination prevention tests
```

**Structure Decision**: The implementation will extend the existing backend service with new RAG capabilities. This allows the RAG functionality to reuse existing database connections, configuration, and authentication patterns while providing dedicated endpoints for query processing.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [Complex orchestration] | Need to coordinate multiple services (embedding, vector search, DB retrieval, LLM) | Single monolithic function would be harder to test and maintain |
