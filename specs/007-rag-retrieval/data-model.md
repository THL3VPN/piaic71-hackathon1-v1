# Data Model: RAG Retrieval

## Entities

### Query
- **query_id**: UUID (Primary Key)
- **user_question**: String (Original user question)
- **embedded_query**: JSON (Vector representation of the question)
- **top_k**: Integer (Number of top results to retrieve)
- **created_at**: DateTime (Timestamp of query creation)

### RetrievalResult
- **result_id**: UUID (Primary Key)
- **query_id**: UUID (Foreign Key to Query)
- **chunk_ids**: Array of UUIDs (IDs of retrieved chunks)
- **confidence_scores**: Array of Floats (Similarity scores for each retrieved chunk)
- **retrieved_at**: DateTime (Timestamp of retrieval)
- **retrieval_time_ms**: Integer (Time taken for retrieval in milliseconds)

### ContextBundle
- **bundle_id**: UUID (Primary Key)
- **query_id**: UUID (Foreign Key to Query)
- **retrieved_chunks**: JSON (Complete chunks with content and metadata)
- **formatted_context**: Text (Formatted context with citations)
- **token_count**: Integer (Number of tokens in the context)
- **created_at**: DateTime (Timestamp of bundle creation)

### Citation
- **citation_id**: UUID (Primary Key)
- **bundle_id**: UUID (Foreign Key to ContextBundle)
- **chunk_id**: UUID (Foreign Key to retrieved Chunk)
- **source_path**: String (Path to the source document)
- **heading**: String (Heading where chunk appears)
- **chunk_index**: Integer (Index of chunk in document)
- **citation_text**: Text (Formatted citation string)

### RetrievalStatistics
- **stat_id**: UUID (Primary Key)
- **query_pattern**: String (Pattern of queries for analytics)
- **success_count**: Integer (Number of successful retrievals)
- **failure_count**: Integer (Number of failed retrievals)
- **avg_response_time**: Float (Average response time in milliseconds)
- **last_accessed**: DateTime (Last time this pattern was accessed)

## Relationships
- Query (1) → (Many) RetrievalResult (via query_id foreign key)
- Query (1) → (One) ContextBundle (via query_id foreign key)
- ContextBundle (1) → (Many) Citation (via bundle_id foreign key)

## Validation Rules
- Query user_question must not be empty
- top_k parameter must be between 1 and 20
- Confidence scores must be between 0 and 1
- Token count must not exceed model context window limits
- Citations must reference valid chunks in the database