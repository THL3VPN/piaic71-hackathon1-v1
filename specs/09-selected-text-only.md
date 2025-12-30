# Feature: Selected Text Only Mode

## Endpoint
### POST `/api/v1/chat/selected`
Request:
- selected_text (string)
- question (string)

Response:
- answer (string)

## Requirements
- MUST NOT call Qdrant or retrieval.
- Model must answer using ONLY selected_text.
- If selected_text insufficient, respond clearly that provided text is not enough.

## Acceptance Criteria
- Tests enforce no retrieval calls (mock/spy).
- Responses refuse when question requires external context.
