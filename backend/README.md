# Backend Service

FastAPI service for the project.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

## Running the Service

To run the service locally:

```bash
uvicorn src.main:app --reload
```

Or with uv:

```bash
uv run python src/main.py
```

## Testing

To run tests:

```bash
python -m pytest tests/
```