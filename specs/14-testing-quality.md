# Feature: Testing & Quality Gates

## Requirements
- Use pytest for all backend testing.
- Enforce minimum 80% coverage for backend.
- CI should run tests and fail on:
  - test failure
  - coverage below 80%

## Acceptance Criteria
- `uv run pytest --cov` achieves >= 80%.
- CI config exists and is documented.
