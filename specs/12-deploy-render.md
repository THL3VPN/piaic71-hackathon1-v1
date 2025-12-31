# Feature: Deploy Backend to Render

## Requirements
- Provide Render deployment guidance:
  - start command using uv + uvicorn
  - required environment variables
- Ensure CORS includes GitHub Pages origin.
- Provide `/health` and `/ready` for Render health checks.

## Acceptance Criteria
- Backend deploys and is reachable publicly.
- Book can successfully call backend from GitHub Pages.
