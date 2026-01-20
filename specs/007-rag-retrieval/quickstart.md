# Quickstart: RAG Retrieval Implementation

## Prerequisites
- Python 3.11+
- uv package manager
- Access to Neon PostgreSQL database
- Access to Qdrant vector database
- Environment variables configured (.env file)

## Setup
1. Ensure all required environment variables are set in `.env`:
   ```
   NEON_DATABASE_URL=...
   QDRANT_URL=...
   QDRANT_API_KEY=...
   OPENAI_API_KEY=...  # Or equivalent for your chosen LLM provider
   ```

2. Install dependencies:
   ```bash
   cd backend
   uv pip install -r requirements.txt
   ```

## Usage
Query the RAG system using the API endpoint:
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Your question about the book content",
    "top_k": 5,
    "include_citations": true
  }'
```

## Configuration
The system can be configured with:
- `top_k`: Number of top results to retrieve (default: 5)
- `similarity_threshold`: Minimum similarity score for inclusion (default: 0.5)
- `max_context_tokens`: Maximum tokens in context bundle (default: 3000)

## Output
The system provides:
- Grounded answers based on book content
- Citations showing source_path, heading, and chunk_index
- Confidence scores for retrieved chunks
- Performance metrics for query processing