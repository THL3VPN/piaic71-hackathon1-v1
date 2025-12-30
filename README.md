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
The documentation site is built with Docusaurus and can be built and deployed to GitHub Pages.

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
The backend service is built with FastAPI and can be run locally with uv.

To run locally:
```bash
cd backend
source .venv/bin/activate
uv run python src/main.py
```

To run tests:
```bash
cd backend
source .venv/bin/activate
python -m pytest tests/
```

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