# Quickstart Guide: Monorepo Layout

## Overview
This guide provides quick instructions for setting up and working with the monorepo layout containing documentation, frontend, and backend components.

## Prerequisites
- Node.js >= 20.0
- Python >= 3.11
- uv package manager
- Git

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
   yarn install
   cd ..

   # Navigate to backend directory and install dependencies
   cd backend
   uv pip install -r requirements.txt
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
   yarn start
   ```

3. Build for production:
   ```bash
   yarn build
   ```

4. Deploy to GitHub Pages:
   ```bash
   GIT_USER=<your-github-username> yarn deploy
   ```

### Backend (backend/)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Start the development server with uv:
   ```bash
   uv run python src/main.py
   ```

3. Run tests:
   ```bash
   python -m pytest tests/
   ```

### Frontend (frontend/)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   yarn install
   ```

3. Start development server:
   ```bash
   yarn start
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
- If backend fails to start, check that all dependencies are installed and environment variables are set
- If frontend fails to build, verify all dependencies are installed and paths are correct