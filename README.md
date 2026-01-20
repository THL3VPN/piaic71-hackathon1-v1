# PIAIC71-Hackathon1-v1

This is the main repository for the PIAIC71 Hackathon project. This monorepo contains multiple components for a comprehensive documentation and AI integration system.

## Repository Structure

- `/book` - Docusaurus documentation site
- `/frontend` - Reusable UI components
- `/backend` - FastAPI service
- `/specs` - Feature specifications
- `/adrs` - Architecture decision records

## Getting Started

### Prerequisites

- Node.js >= 20.0
- Python >= 3.11
- uv package manager
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Initialize all components:
   ```bash
   # Navigate to book directory and install dependencies
   cd book
   npm install
   cd ..

   # Navigate to backend directory and install dependencies
   cd backend
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   cd ..
   ```

## Components

### Documentation (book/)
The documentation site is built with Docusaurus and can be built and deployed to GitHub Pages. It contains comprehensive coverage of Physical AI and robotics technologies organized into four main modules:

- **ROS 2**: Robot Operating System 2 fundamentals and applications
- **Gazebo & Unity**: Simulation environments for robotics and AI
- **NVIDIA Isaac**: NVIDIA's platform for robotics and AI applications
- **Vision-Language-Action (VLA)**: Advanced models for perception and action

Additionally, you'll find course-wide information covering learning outcomes, assessments, and hardware requirements.

To run locally:
```bash
cd book
npm start
```

To build:
```bash
cd book
npm run build
```

### Backend (backend/)
The backend service is built with FastAPI and provides health and readiness endpoints, configuration validation, and CORS support for GitHub Pages integration. It includes a comprehensive database schema with PostgreSQL/Neon support for documents, chunks, chat sessions, chat messages, and ingestion jobs. The service also includes a CLI for document ingestion.

Key features:
- **Health endpoint**: `/health` returns service status
- **Readiness endpoint**: `/ready` checks external dependencies (Neon, Qdrant)
- **CORS configuration**: Allows requests from GitHub Pages origins
- **Configuration validation**: Validates environment variables at startup
- **Database support**: PostgreSQL/Neon with Alembic migrations
- **Data models**: Documents, chunks, chat sessions, chat messages, and ingestion jobs
- **Dependency management**: Uses uv for Python package management
- **Document Ingestion CLI**: Command-line interface for processing documents from book/docs directory, extracting text, chunking, and storing to Neon and Qdrant

To run locally:
```bash
cd backend
source .venv/bin/activate  # If using virtual environment
uv run uvicorn app.main:app --reload
```

To run tests:
```bash
cd backend
source .venv/bin/activate  # If using virtual environment
uv run pytest tests/
```

To use the document ingestion CLI:
```bash
cd backend
source .venv/bin/activate  # If using virtual environment
uv run python -m app.cli.ingestion ingest
```

Additional CLI options:
```bash
# Run incremental ingestion (skip unchanged documents)
uv run python -m app.cli.ingestion ingest --incremental

# Specify a different directory to scan
uv run python -m app.cli.ingestion ingest --directory /path/to/docs

# Enable verbose logging
uv run python -m app.cli.ingestion ingest --verbose

# Validate configuration before running ingestion
uv run python -m app.cli.ingestion validate-config
```

Database setup:
1. Copy the environment file: `cp backend/.env.example backend/.env`
2. Update `backend/.env` with your Neon database credentials
3. Run database migrations: `cd backend && uv run alembic upgrade head`

The database schema includes the following tables:
- `documents`: Stores document metadata and references
- `chunks`: Stores document chunks with content and metadata
- `chat_sessions`: Tracks chat conversation sessions
- `chat_messages`: Stores individual chat messages within sessions
- `ingestion_jobs`: Tracks document ingestion job status and progress

Environment variables can be configured in `.env` file (copy from `.env.example`).

### Qdrant Vector Database Integration

The backend service includes integration with Qdrant vector database for document similarity search:

- **Qdrant Collection**: `book_chunks` stores document chunks with vector embeddings
- **Configuration**: Set Qdrant connection parameters in `.env` file
- **Endpoints**:
  - `/api/chunks/vector`: Upsert document chunk vectors
  - `/api/search/vector`: Perform vector similarity search
  - `/health/qdrant`: Check Qdrant connectivity and collection status
- **Features**:
  - Configurable vector dimensions and distance metrics
  - UUID-based chunk identification
  - Rich metadata storage (document_id, source_path, title, chunk_index)
  - Payload size validation to avoid Qdrant limits

### Frontend (frontend/)
Reusable UI components for the project.

To run:
```bash
cd frontend
npm install
npm start
```

## Development

For detailed development instructions, see the quickstart guide in `specs/001-monorepo-layout/quickstart.md`.

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Commit with descriptive messages
4. Push changes and create a pull request

## Security

- The `.gitignore` file is configured to ignore secrets and temporary files
- The `.env` file is ignored but `.env.example` is included in version control
- Always verify that sensitive information is not committed