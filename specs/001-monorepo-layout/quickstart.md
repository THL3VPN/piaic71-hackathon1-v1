# Quickstart Guide: Monorepo Layout

## Overview
This guide provides quick instructions for setting up and working with the monorepo layout containing documentation, frontend, and backend components.

## Prerequisites
- Node.js >= 20.0
- Python >= 3.11
- uv package manager
- Git
- PostgreSQL (for production) or Docker for local development

## Repository Setup
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

   # Navigate to frontend directory and install dependencies
   cd frontend
   npm install
   cd ..
   ```

## Working with Components

### Documentation (book/)
1. Navigate to the book directory:
   ```bash
   cd book
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

4. Deploy to GitHub Pages:
   ```bash
   GIT_USER=<your-github-username> npm run deploy
   ```

### Backend (backend/)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment and install dependencies:
   ```bash
   uv venv  # Create virtual environment if not already created
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. Database Setup:
   - For development: SQLite is used automatically for testing
   - For production: PostgreSQL with Neon database is configured
   - Copy the environment file and update with your Neon credentials:
     ```bash
     cd backend
     cp .env.example .env
     # Edit .env with your Neon database credentials
     ```
   - Key environment variables for Neon database:
     ```bash
     # In backend/.env file
     NEON_DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
     DATABASE_USER=your_db_user
     DATABASE_PASSWORD=your_db_password
     DATABASE_HOST=ep-xxx.region.aws.neon.tech
     DATABASE_PORT=5432
     DATABASE_NAME=your_db_name
     ```

4. Database Schema and Migrations:
   - The database includes the following tables for document management and chat functionality:
     - `documents`: Stores document metadata and references
     - `chunks`: Stores document chunks with content and metadata
     - `chat_sessions`: Tracks chat conversation sessions
     - `chat_messages`: Stores individual chat messages within sessions
     - `ingestion_jobs`: Tracks document ingestion job status and progress
   - Initialize the database with Alembic:
     ```bash
     # For offline operations (schema generation, no DB connection needed):
     cd backend
     source .venv/bin/activate
     uv run alembic upgrade head --sql

     # For online operations with Neon database:
     # 1. Make sure your .env file contains the database configuration:
     #    cp .env.example .env
     #    # Edit .env with your Neon database credentials

     # 2. Run the migration (Alembic will automatically load .env variables):
     uv run alembic upgrade head

     # Or use the provided migration script:
     ./migrate_to_neon.sh
     ```
   - Create new migrations:
     ```bash
     # When you make changes to models
     uv run alembic revision --autogenerate -m "Description of changes"
     uv run alembic upgrade head
     ```

5. Start the development server with uvicorn:
   ```bash
   source .venv/bin/activate
   uv run uvicorn app.main:app --reload
   ```

6. The backend service provides the following endpoints:
   - Health check: `GET /health` - Returns service status
   - Readiness check: `GET /ready` - Checks external dependencies (Neon, Qdrant)
   - Root endpoint: `GET /` - Returns service information

7. Run tests:
   ```bash
   source .venv/bin/activate
   uv run pytest tests/
   ```

8. Run specific tests:
   ```bash
   # Run all tests
   uv run pytest

   # Run specific test file
   uv run pytest tests/test_health.py

   # Run with verbose output
   uv run pytest -v
   ```

### Frontend (frontend/)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

## Environment Configuration
1. Create a `.env` file in the backend directory:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

## Git Configuration
- The `.gitignore` file is already configured to ignore secrets and temporary files
- The `.env` file is ignored but `.env.example` is included in version control
- Always verify that sensitive information is not committed

## Development Workflow
1. Create a new branch for your feature:
   ```bash
   git checkout -b <feature-branch-name>
   ```

2. Work on the appropriate component directory

3. Commit changes with descriptive messages:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

4. Push changes and create a pull request

## Troubleshooting
- If documentation build fails, ensure all markdown files have proper frontmatter
- If backend fails to start, check that the virtual environment is activated and all dependencies are installed
- If frontend fails to build, verify all dependencies are installed and paths are correct
- If you encounter dependency issues, ensure you're using the correct package manager (npm for frontend/book, uv for backend)