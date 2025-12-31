# Feature: RAG Retrieval (Book-only)

## Requirements
- Retrieval must use ONLY chunks derived from `/book/docs`.
- Retrieval flow:
  1) embed question
  2) vector search in Qdrant (top_k configurable)
  3) fetch chunk_text and metadata from Neon by chunk ids
  4) build context with citations (source_path + heading + chunk_index)
- Prompt must instruct model to answer grounded in context and to refuse if insufficient.

## Acceptance Criteria
- Given known questions, system returns relevant chunks.
- If retrieval returns low confidence / empty, assistant responds with insufficient info (no hallucination).
- Unit tests cover:
  - retrieval query building
  - citation formatting
  - refusal behavior when no context
