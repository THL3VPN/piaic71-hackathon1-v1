# Feature: Monorepo Layout

## Requirements
- Repo contains:
  - `/book` Docusaurus site
  - `/frontend` reusable UI components
  - `/backend` FastAPI service
  - `/specs` specs
  - `/adrs` architecture decision records

## Acceptance Criteria
- `book` builds and deploys to GitHub Pages.
- `backend` can run locally with uv.
- Git ignores secrets; `.env.example` exists for backend.
