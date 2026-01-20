# Research Findings: RAG Retrieval Implementation

## Decision: Embedding Model Selection
**Rationale**: Using Sentence Transformers with a pre-trained model (e.g., all-MiniLM-L6-v2) for question and document embedding to ensure consistency between query and document embeddings
**Alternatives considered**: OpenAI embeddings, HuggingFace transformers, custom models - Sentence Transformers provides good performance with minimal setup

## Decision: Vector Search Configuration
**Rationale**: Using Qdrant's cosine similarity with configurable top_k parameter to allow system administrators to tune the number of results returned
**Alternatives considered**: Euclidean distance, dot product - Cosine similarity is most appropriate for semantic search

## Decision: Citation Format
**Rationale**: Including source_path, heading, and chunk_index in citations to provide complete reference information for users to verify information
**Alternatives considered**: Just source_path, source + line numbers - Full citation provides most context for verification

## Decision: Hallucination Prevention Strategy
**Rationale**: Implementing strict grounding with refusal mechanism when confidence is low or no relevant chunks are found, preventing the LLM from generating answers without proper context
**Alternatives considered**: Confidence thresholding, partial answers - Complete refusal ensures no hallucinated information

## Decision: Context Building Approach
**Rationale**: Building context bundles with retrieved chunks and citations, then passing to LLM with specific instructions to ground responses in provided context
**Alternatives considered**: Direct chunk insertion, multi-turn conversation - Bundled context approach provides cleaner separation of concerns