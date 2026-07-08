# backend_v3 Frontend Integration Guide

This guide describes how frontend clients should call `backend_v3` APIs and handle responses consistently.

## 1. Base URL and Headers

- Base path: `/api`
- Content type: `application/json`
- Optional request correlation header: `X-Request-ID`

Example:

```http
POST /api/generate/flashcards
Content-Type: application/json
X-Request-ID: 9f4a2e07-3f1c-4e28-a6ef-8e9b2f3e1abc
```

---

## 2. Endpoint Overview

- `GET /api/health`
- `POST /api/pipeline/run`
- `POST /api/generate/flashcards`
- `POST /api/generate/quiz`
- `POST /api/generate/summary`

---

## 3. Health Check

### Request

```http
GET /api/health
```

### Response

```json
{
  "status": "ok"
}
```

---

## 4. Pipeline API (`/api/pipeline/run`)

Use this API for ingestion and processing (parse, chapters, chunks, embeddings, vector storage, summary/index).

### 4.1 Request Body (full run)

```json
{
  "document_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
  "user_id": "8778953d-f997-49b0-8ba1-797520cc9a14",
  "subject_id": "7bcf9dd0-d8ff-4ac5-9c2e-c5ea9dbf2d8b",
  "document_type": "pdf",
  "file_path": "C:/path/to/file.pdf",
  "debug": true
}
```

### 4.2 Stage-Range Request (recommended in UI for controlled flows)

```json
{
  "document_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
  "user_id": "8778953d-f997-49b0-8ba1-797520cc9a14",
  "subject_id": "7bcf9dd0-d8ff-4ac5-9c2e-c5ea9dbf2d8b",
  "document_type": "pdf",
  "file_path": "C:/path/to/file.pdf",
  "from": "validate_input",
  "to": "build_document_index",
  "debug": true
}
```

### 4.3 Response (shape)

```json
{
  "request_id": "8ed00864-8537-4b65-b0b3-09cb8ab29c83",
  "document_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
  "executed_stages": [
    "validate_input",
    "parse_document",
    "detect_chapters",
    "split_chunks",
    "generate_embeddings",
    "store_vectors",
    "build_document_index"
  ],
  "stage_results": [
    { "stage": "parse_document", "ok": true, "details": { "total_pages": 21 } }
  ],
  "output": {}
}
```

Notes:
- `build_document_index` persists a summary into `documents.content_text`.
- Keep `user_id` present when stages include vector storage.

---

## 5. Flashcards API (`/api/generate/flashcards`)

### 5.1 Request Body (recommended)

```json
{
  "scope": "document",
  "scope_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
  "query": "business model canvas",
  "user_id": "8778953d-f997-49b0-8ba1-797520cc9a14",
  "count": 8,
  "prompt_profile": "concise",
  "front_max_chars": 90,
  "back_max_chars": 220,
  "save": true,
  "debug": true
}
```

### 5.2 Required Fields

- `scope`: `subject | document | chapter | summary`
- `scope_id`
- `query` (required; minimum 3 chars)

### 5.3 Response (shape)

```json
{
  "flashcards": [
    { "front": "What is BMC?", "back": "A strategic template for business model design." }
  ],
  "sources": [
    {
      "document_type": "pdf",
      "page": 2,
      "chapter_name": null,
      "preview": "Business Model Canvas ..."
    }
  ],
  "diagnostics": {
    "scope": "document",
    "scope_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
    "query": "business model canvas",
    "total_candidates": 5,
    "accepted_candidates": 4,
    "best_score": 1.0,
    "debug_trace_id": "48a23ae4-6235-477c-8142-41ff85b7ceb0",
    "debug_artifact_path": ".debug_runs/generation_...json",
    "context_scores": []
  }
}
```

Behavior:
- Context combines persisted document summary + retrieved chunks when available.
- If `save=true`, generated payload is persisted into `generated_content`.

---

## 6. Quiz API (`/api/generate/quiz`)

### 6.1 Request Body (recommended)

```json
{
  "scope": "document",
  "scope_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
  "query": "value proposition and customer segments",
  "user_id": "8778953d-f997-49b0-8ba1-797520cc9a14",
  "count": 10,
  "difficulty": "medium",
  "prompt_profile": "exam",
  "question_max_chars": 180,
  "explanation_max_chars": 260,
  "save": true,
  "debug": true
}
```

### 6.2 Response (shape)

```json
{
  "questions": [
    {
      "question": "Which statement best describes value proposition?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": 1,
      "explanation": "It defines the value delivered to target segments.",
      "source": {
        "document_type": "pdf",
        "page": 4,
        "chapter_name": null,
        "preview": "..."
      }
    }
  ],
  "diagnostics": {
    "scope": "document",
    "scope_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
    "query": "value proposition and customer segments",
    "total_candidates": 5,
    "accepted_candidates": 3,
    "best_score": 0.9,
    "debug_trace_id": "...",
    "debug_artifact_path": "...",
    "context_scores": []
  }
}
```

Behavior:
- Same grounding logic as flashcards (summary + chunks).
- If `save=true`, quiz payload is persisted in `generated_content`.

---

## 7. Summary API (`/api/generate/summary`)

Returns persisted summary from `documents.content_text`.

### Request

```json
{
  "scope_id": "a650b078-5c2a-4b12-b183-bed91dad3a34",
  "user_id": "8778953d-f997-49b0-8ba1-797520cc9a14"
}
```

### Response

```json
{
  "summary": "...",
  "scope": "summary",
  "scope_id": "a650b078-5c2a-4b12-b183-bed91dad3a34"
}
```

---

## 8. Error Handling Contract

### 8.1 AppError shape

```json
{
  "error": "insufficient_context",
  "message": "Insufficient context for topic",
  "details": { "scope": "document", "scope_id": "..." },
  "request_id": "..."
}
```

### 8.2 Common Cases

- `insufficient_context` (400): retrieval found nothing usable.
- `summary_not_found` (404): no persisted summary for the document.
- `invalid_generation_output` (502): model output failed schema/parse after retry.
- `validation_error` (400): pipeline input missing/invalid.
- FastAPI validation (422): missing required request fields (e.g., missing `query` for quiz/flashcards).

---

## 9. Frontend Integration Recommendations

1. Always pass `query` for flashcards/quiz.
2. Keep prompts backend-owned; use request controls instead:
   - `prompt_profile`, `count`, `difficulty`, max chars.
3. Use `save=true` for generation history.
4. For ingestion UI, run pipeline until `build_document_index` before allowing generation.
5. Show diagnostics and source previews in UI for transparency.
6. Pass `X-Request-ID` from frontend to correlate logs/errors.

---

## 10. Minimal TypeScript Client Example

```ts
const res = await fetch('/api/generate/flashcards', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Request-ID': crypto.randomUUID(),
  },
  body: JSON.stringify({
    scope: 'document',
    scope_id: documentId,
    query: 'business model canvas',
    user_id: userId,
    count: 6,
    prompt_profile: 'concise',
    front_max_chars: 90,
    back_max_chars: 220,
    save: true,
    debug: true,
  }),
})

if (!res.ok) {
  const err = await res.json()
  throw new Error(`${err.error}: ${err.message}`)
}

const data = await res.json()
```

---

## 11. Quick Operational Checklist

- Ingested document includes vectors and summary (`build_document_index` stage done).
- `query` is present for flashcards/quiz.
- `scope_id` belongs to calling user context.
- `save=true` if history is required.
- For troubleshooting, use `request_id` + `debug_trace_id`.
