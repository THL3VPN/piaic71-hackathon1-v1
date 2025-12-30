# Feature: Qdrant Collections

## Requirements
- Create a Qdrant collection for book chunks, e.g. `book_chunks`.
- Each point id must map 1:1 to chunk id (uuid as string).
- Store payload fields:
  - document_id
  - source_path
  - title
  - chunk_index
- Vector size and distance metric are configurable (env vars).

## Acceptance Criteria
- A readiness check can confirm collection exists and is reachable.
- Ingestion can upsert points deterministically by chunk id.
