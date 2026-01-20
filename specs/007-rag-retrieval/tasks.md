# Implementation Tasks: RAG Retrieval (Book-only)

**Feature**: RAG Retrieval | **Branch**: `007-rag-retrieval` | **Spec**: [spec.md](spec.md)

## Dependencies & Parallel Execution

### User Story Completion Order
1. US1: Query Book Content with Contextual Citations (P1)
2. US2: Handle Low-Confidence or Empty Retrieval (P1)
3. US3: Configure Retrieval Parameters (P2)

### Parallel Execution Examples
- **US1 & US2**: Can be developed in parallel since US2 builds on US1's core functionality
- **API endpoints & services**: API development can happen in parallel with service implementation
- **Testing & implementation**: Test creation can happen in parallel with implementation

## Implementation Strategy

**MVP Scope**: US1 (Query with Citations) + US2 (Handle Low Confidence) = Core RAG functionality that prevents hallucination

**Incremental Delivery**:
1. Phase 1-2: Core infrastructure and setup
2. Phase 3: US1 - Basic query and citation functionality
3. Phase 4: US2 - Hallucination prevention
4. Phase 5: US3 - Configuration management
5. Phase 6: Polish and cross-cutting concerns

---

## Phase 1: Setup Tasks

### Goal
Initialize project structure and install required dependencies for the RAG system.

- [X] T001 Install required dependencies: fastapi, qdrant-client, sqlalchemy, openai/anthropic, sentence-transformers, uv
- [X] T002 Set up configuration for RAG parameters (top_k, similarity_threshold, etc.)

## Phase 2: Foundational Tasks

### Goal
Create foundational components that are required by multiple user stories.

- [X] T003 Create Query model in backend/app/models/query.py based on data model
- [X] T004 Create RetrievalResult model in backend/app/models/retrieval_result.py based on data model
- [X] T005 Create ContextBundle model in backend/app/models/context_bundle.py based on data model
- [X] T006 Create Citation model in backend/app/models/citation.py based on data model
- [X] T007 Create embedding service in backend/app/services/embedding_service.py
- [X] T008 Create retrieval service in backend/app/services/retrieval_service.py
- [X] T009 Create citation service in backend/app/services/citation_service.py
- [X] T010 Create context builder utility in backend/app/utils/context_builder.py
- [X] T011 Create hallucination guard utility in backend/app/utils/hallucination_guard.py
- [X] T012 Create retrieval repository in backend/app/database/retrieval_repository.py

## Phase 3: [US1] Query Book Content with Contextual Citations

### Goal
Allow users to ask questions about book content and receive answers with citations showing where information originated.

**Independent Test**: Can ask known questions about book content and verify system returns relevant chunks with proper citations.

- [X] T013 [P] [US1] Create RAG API endpoints in backend/app/api/rag.py
- [X] T014 [P] [US1] Create RAG request/response models in backend/app/api/models.py
- [X] T015 [US1] Implement embedding service to convert questions to vectors
- [X] T016 [US1] Extend Qdrant service for vector similarity search with configurable top_k
- [X] T017 [US1] Implement chunk retrieval from Neon using chunk IDs returned by Qdrant
- [X] T018 [US1] Build context with citations including source_path, heading, and chunk_index
- [X] T019 [US1] Create RAG orchestration service in backend/app/services/rag_service.py
- [X] T020 [US1] Format citations properly with source_path, heading, and chunk_index
- [X] T021 [US1] Add retrieval statistics tracking in retrieval repository
- [X] T022 [US1] Implement basic query processing with grounding in context
- [X] T023 [US1] Add RAG retrieval tests in backend/tests/test_retrieval.py

## Phase 4: [US2] Handle Low-Confidence or Empty Retrieval

### Goal
Prevent hallucination by clearly indicating when the system cannot find relevant information.

**Independent Test**: Ask questions with no relevant book content and verify system refuses to answer rather than hallucinating.

- [X] T024 [P] [US2] Implement confidence threshold checking in retrieval service
- [X] T025 [P] [US2] Implement hallucination guard to prevent answers without proper context
- [X] T026 [US2] Return appropriate response when retrieval confidence is low
- [X] T027 [US2] Return appropriate response when no relevant chunks are found
- [X] T028 [US2] Implement refusal behavior when insufficient context is available
- [X] T029 [US2] Validate that no hallucinated answers are generated
- [X] T030 [US2] Add proper error messaging for insufficient information cases
- [X] T031 [US2] Add hallucination prevention tests in backend/tests/test_hallucination_guard.py

## Phase 5: [US3] Configure Retrieval Parameters

### Goal
Allow system administrators to configure retrieval parameters like top_k for optimization.

**Independent Test**: Adjust top_k configuration and verify vector search returns configured number of results.

- [X] T032 [P] [US3] Make top_k parameter configurable via settings
- [X] T033 [P] [US3] Make similarity_threshold configurable via settings
- [X] T034 [US3] Implement configurable context size limits
- [X] T035 [US3] Add validation for configurable parameters
- [X] T036 [US3] Update API endpoints to accept optional configuration overrides
- [X] T037 [US3] Add parameter validation and error handling
- [X] T038 [US3] Add configuration parameter tests in backend/tests/

## Phase 6: Polish & Cross-Cutting Concerns

### Goal
Add finishing touches, error handling, and integration validation.

- [X] T039 Add comprehensive error handling for all edge cases (embedding failures, database unavailability, etc.)
- [X] T040 Implement memory management for large context building
- [X] T041 Add logging throughout the RAG pipeline
- [X] T042 Create integration tests covering the full RAG pipeline in backend/tests/test_rag.py
- [X] T043 Document the API usage and configuration in quickstart.md
- [X] T044 Run full RAG pipeline test with sample queries
- [X] T045 Add citation formatting tests in backend/tests/test_citations.py