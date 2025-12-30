# Feature: Embed Chat + Selection UI in Docusaurus

## Requirements
- Embed the chat widget across book pages (global).
- Add “Ask about selection”:
  - user highlights text in chapter
  - UI offers action to open widget in selected-text mode
- Backend base URL must be configurable (env or config file).

## Acceptance Criteria
- Deployed book can chat with deployed backend.
- Selection flow triggers `/api/v1/chat/selected` and displays answer.
