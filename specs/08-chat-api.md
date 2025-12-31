# Feature: Chat API (RAG)

## Endpoints
### POST `/api/v1/chat`
Request:
- session_id (optional uuid)
- message (string)

Response:
- session_id (uuid)
- answer (string)
- citations (array)
  - source_path
  - title
  - chunk_index
  - snippet (short)

## Requirements
- Must store session + messages in Neon.
- Must return citations from retrieved chunks.
- Must enforce "book-only" grounding.

## Acceptance Criteria
- API responds within reasonable time locally.
- Tests validate:
  - schema validation
  - session creation
  - citations presence when context exists
