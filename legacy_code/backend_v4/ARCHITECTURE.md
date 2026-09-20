# backend_v4 Architecture

## 1. Architectural Style

- Backend framework: FastAPI (Python).
- Core pattern: layered architecture + explicit ports/adapters.
- Processing model: asynchronous ingestion, synchronous query/generation with optional streaming.

Layers:

- presentation: API routes, request/response DTO validation.
- application: use cases, orchestrators, feature-flag routing.
- domain: entities, value objects, policies, interfaces.
- infrastructure: vector DB, graph DB, LLM/embedding providers, file parsers.

## 2. Core Subsystems

### 2.1 Ingestion Subsystem

Pipeline stages:

1. input validation
2. document parse (PDF or text summary)
3. chapter/section detection
4. semantic chunking
5. embedding generation
6. vector persistence
7. summary tree generation (RAPTOR-style recursive summaries)
8. optional triplet extraction for graph index

Output artifacts:

- chunk records with metadata
- document summary hierarchy
- optional graph entities/relations

### 2.2 Retrieval Subsystem

Routing by intent:

- Direct factual query -> vector/hybrid retrieval.
- Global synthesis query -> summary tree + graph context.
- Action request (flashcards/quiz) -> educational generation pipeline.

Retrieval flow:

1. retrieve candidates from vector + lexical sources
2. merge candidates
3. rerank top candidates
4. build compact grounded context package
5. return retrieval diagnostics

### 2.3 Generation Subsystem

Endpoints:

- generate summary
- generate flashcards
- generate quiz

Controls:

- strict JSON schema for structured outputs
- prompt profile support (concise, exam, conceptual)
- one validation retry on malformed generation
- source citation per generated item when available

### 2.4 Optional Agentic Subsystem

- Enabled only when ENABLE_AGENTIC_RAG=true.
- Planner decides tool sequence for complex requests.
- Evaluator validates generated outputs against retrieved evidence.
- Fallback to deterministic mode when confidence is low.

## 3. Data Storage

Recommended baseline:

- PostgreSQL/Supabase for metadata and generated content.
- Qdrant for vector index (local Docker friendly).
- Neo4j for graph index (optional for phase 2+).

Minimal entities:

- documents
- document_chunks
- summary_nodes
- graph_entities
- graph_relations
- generated_content
- pipeline_runs

## 4. Feature Flags

- ENABLE_HYBRID_RETRIEVAL
- ENABLE_SUMMARY_INDEX
- ENABLE_GRAPH_RAG
- ENABLE_AGENTIC_RAG
- ENABLE_DEBUG_ENDPOINTS

## 5. Observability

Required telemetry per request:

- request_id
- user_id (if available)
- scope_id
- stage
- duration_ms
- retrieved_count
- prompt_tokens
- completion_tokens
- estimated_cost

Debug artifacts per pipeline run:

- parsed content snapshot
- chunk and chapter outputs
- retrieval candidates and scores
- final context package
- validation errors and retries

## 6. Security and Governance

- row-level security enforced for user-owned content.
- secret management only through environment variables.
- redaction policy for logs that may include document excerpts.
- audit-ready generation metadata (model, timestamp, source ids).
