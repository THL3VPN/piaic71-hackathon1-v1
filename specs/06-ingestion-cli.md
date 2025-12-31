# Feature: Ingestion CLI (Docs → Chunks → Embeddings → Qdrant + Neon)

## Requirements
- Provide CLI entry in backend using:
  - Typer (commands)
  - Questionary (interactive prompts)
  - Rich (output)
- Command: `ingest` that:
  1) reads all files under `../book/docs`
  2) extracts clean text from MD/MDX (keep code blocks; strip frontmatter)
  3) chunks text with deterministic strategy
  4) writes documents + chunks to Neon
  5) computes embeddings
  6) upserts vectors to Qdrant using chunk ids
- Support incremental ingestion using checksum:
  - skip unchanged docs
  - update changed docs and affected chunks

## Acceptance Criteria
- `uv run python -m app.cli ingest` runs successfully when env vars set.
- Re-running ingestion does not duplicate unchanged chunks.
- CLI produces clear progress output and a final summary.
