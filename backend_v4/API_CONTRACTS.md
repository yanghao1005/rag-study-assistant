# backend_v4 API Contracts (Frontend-Aligned Draft v2)

This contract is aligned to the current frontend client and types in frontend/src.

## 1. Base URL and Headers

- Frontend runtime base URL: NEXT_PUBLIC_API_BASE_URL
- Default value in frontend env: <http://localhost:8000/api>
- API prefix expected by frontend: /api

Required request headers:

- Content-Type: application/json (except FormData requests)
- Authorization: Bearer <supabase_access_token> when user session exists

Optional request header:

- X-Request-ID: frontend may send for correlation

## 2. Health Endpoint

GET /health

Response:
{
  "status": "ok"
}

## 3. Pipeline Endpoint (Debug/Operations)

POST /pipeline/run

Request body:

- document_id: string (required)
- file_path: string (required, server-reachable path)
- user_id?: string
- stage: string | null
- from: string | null
- to: string | null
- debug: boolean

Supported stage names:

- validate_input
- parse_document
- detect_sections
- semantic_chunking
- build_embeddings
- persist_vectors
- build_summary_index
- extract_graph_triplets

## 3.1 Documents Upload Endpoint

POST /documents/upload

Request body (multipart/form-data):

- file: file (required; .pdf, .txt, .md)
- subject_id: string (required)
- user_id: string (required)

Response body:

- document_id: string
- filename: string
- file_path: string
- status: ready | error

## 3.2 Summary Ingestion Endpoint

POST /documents/summary

Request body (application/json):

- subject_id: string (required)
- user_id: string (required)
- title: string (required)
- content: string (required)

Response body:

- document_id: string
- filename: string
- file_path: string
- status: ready | error

## 3.3 Document Download Endpoint

GET /documents/{document_id}/download?user_id={user_id}

Query params:

- user_id: string (required)

Response:

- Binary file stream with attachment headers.
- For uploaded PDFs/TXT/MD: original uploaded content.
- For summary-only records: generated `.txt` content from stored summary text.

Response shape:

- request_id: string | null
- document_id: string
- executed_stages: string[]
- stage_results: object[]
- output: object

## 4. Generation Endpoints

### 4.1 POST /generate/flashcards

Request body:

- scope: subject | document | chapter | summary
- scope_id: string
- count: number
- query?: string
- user_id?: string
- save?: boolean
- prompt_profile?: concise | exam | conceptual
- front_max_chars?: number
- back_max_chars?: number
- debug?: boolean

Response body:

- flashcards: [{ front: string, back: string }]
- sources?: [{ document_type?: pdf | summary, page?: number | null, chapter_name?: string | null, preview?: string | null }]
- diagnostics?: {
  scope: subject | document | chapter | summary,
  scope_id: string,
  query: string,
  total_candidates: number,
  accepted_candidates: number,
  best_score: number,
  debug_trace_id?: string | null,
  debug_artifact_path?: string | null
}

### 4.2 POST /generate/quiz

Request body:

- scope: subject | document | chapter | summary
- scope_id: string
- count: number
- query?: string
- user_id?: string
- save?: boolean
- prompt_profile?: concise | exam | conceptual
- question_max_chars?: number
- explanation_max_chars?: number
- difficulty?: easy | medium | hard
- debug?: boolean

Response body:

- questions: [{
  question: string,
  options: string[],
  correct_answer: number,
  explanation: string,
  source?: { document_type?: pdf | summary, page?: number | null, chapter_name?: string | null, preview?: string | null }
}]
- diagnostics?: same shape as flashcards diagnostics

### 4.3 POST /generate/summary

Request body:

- scope_id: string
- user_id?: string

Response body:

- summary: string
- scope: summary
- scope_id: string

### 4.4 GET /generate/history

Query params:

- user_id: string
- scope: subject | document | chapter | summary
- scope_id: string
- limit?: number (default 8)

Response body:

- items: [{
  id: string,
  user_id: string,
  scope: subject | document | chapter | summary,
  type: string,
  created_at?: string | null,
  subject_id?: string | null,
  document_id?: string | null,
  chapter_id?: string | null,
  content_json: object
}]

## 5. Error Contract

Frontend currently expects:
{
  "error": "string",
  "message": "string",
  "details": {}
}

backend_v4 standard (recommended superset):
{
  "error": "string",
  "message": "string",
  "details": {},
  "request_id": "string"
}

## 6. Compatibility Rules

- Do not use /api/v1 for frontend integration; keep /api prefix.
- Keep request field names exactly as frontend types: scope, scope_id, count, prompt_profile, difficulty.
- Keep optional query behavior for generation endpoints.
- Keep response keys exactly: flashcards, questions, sources, diagnostics, items.
