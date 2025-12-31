# Feature: Neon Postgres Schema (metadata + chat)

## Requirements
Create tables (names can be snake_case):

### documents
- id (uuid pk)
- source_path (text, unique)  # e.g., docs/01-module-1-ros2/01-overview.md
- title (text)
- checksum (text)             # for change detection
- created_at, updated_at

### chunks
- id (uuid pk)
- document_id (fk documents.id)
- chunk_index (int)
- chunk_text (text)
- chunk_hash (text)           # stable per chunk for dedupe
- metadata (jsonb)            # headings, anchors, etc.
- created_at

### ingestion_jobs
- id (uuid pk)
- started_at, finished_at
- status (text)               # running/succeeded/failed
- error (text nullable)
- stats (jsonb)

### chat_sessions
- id (uuid pk)
- created_at

### chat_messages
- id (uuid pk)
- session_id (fk chat_sessions.id)
- role (text)                 # user/assistant/system
- content (text)
- created_at

## Acceptance Criteria
- Migration approach documented (simple SQL migrations is fine).
- Tests verify schema exists / basic insert+select works.
