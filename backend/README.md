# Backend Service

This is the backend service for the PIAIC71-Hackathon1-v1 project. It's built with FastAPI and provides health and readiness endpoints.

## Prerequisites

- Python >= 3.11
- uv package manager
- Node.js >= 20.0 (for potential frontend integration)

## Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt  # For development
   ```

3. Create your environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

## Running the Service

### Development Mode
```bash
source .venv/bin/activate
uv run uvicorn app.main:app --reload --host localhost --port 8000
```

### Production Mode
```bash
source .venv/bin/activate
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /` - Root endpoint returning service information
- `GET /health` - Health check returning service status (always OK if running)
- `GET /ready` - Readiness check verifying external dependencies (Neon, Qdrant)

## Environment Variables

- `BACKEND_HOST` - Host to bind to (default: localhost)
- `BACKEND_PORT` - Port to bind to (default: 8000)
- `NEON_DATABASE_URL` - Connection URL for Neon database
- `QDRANT_URL` - Connection URL for Qdrant vector database
- `GITHUB_PAGES_ORIGIN` - Origin URL for CORS configuration (default: https://your-username.github.io)
- `LOG_LEVEL` - Logging level (default: INFO)
- `REQUEST_TIMEOUT` - Request timeout in milliseconds (default: 30000)

## Testing

Run the test suite:
```bash
source .venv/bin/activate
uv run pytest
```

Run tests with coverage:
```bash
source .venv/bin/activate
uv run pytest --cov=app
```

## Development

1. Make sure your environment is properly configured
2. Create a new branch for your feature
3. Make your changes
4. Run tests to ensure everything works
5. Commit with a descriptive message
6. Push and create a pull request

## Architecture

The backend follows a modular structure:
- `app/main.py` - FastAPI application initialization
- `app/config.py` - Configuration and environment variable validation
- `app/health.py` - Health and readiness endpoints
- `app/dependencies.py` - External dependency connectivity checks
- `app/middleware/` - CORS and other middleware components
- `tests/` - Unit and integration tests

## CORS Configuration

The service is configured to allow requests from GitHub Pages origins to facilitate frontend integration. The configuration is defined in `app/middleware/cors.py`.