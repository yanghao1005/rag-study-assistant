# Project Specification: SmartStudy AI (RAG-based Learning Platform)

## 1. Project Overview
**Goal:** Build a web application that transforms study materials (PDFs and text summaries) into interactive study tools (Flashcards and Quizzes) using Retrieval-Augmented Generation (RAG).
**Context:** This is a Master's Thesis (TFM) in Computer Engineering. The focus is on scalability, clean architecture, and practical AI integration.
**Key Feature:** Users can upload PDFs (textbooks, papers) OR create text summaries (personal notes, condensed materials), then generate study content at multiple levels: entire subject, single document, specific chapter, or individual summary.

## 2. Tech Stack & Architecture

### Frontend (Client)
* **Framework:** Next.js 16+ (App Router).
* **Language:** TypeScript.
* **Styling:** Tailwind CSS.
* **UI Library:** Shadcn/ui (for accessible, professional components).
* **State Management:** React Context API or Zustand (keep it simple but scalable).
* **Networking:** Axios or native Fetch.

### Backend (API)
* **Framework:** FastAPI (Python).
* **Language:** Python 3.10+.
* **AI Orchestration:** LangChain 0.1.x.
* **PDF Parsing:** PyMuPDF (fitz) primary, Unstructured as fallback for scanned PDFs.
* **Validation:** Pydantic models.
* **Environment:** Python `venv` or `poetry`.
* **Monitoring:** Structured logging with request IDs, Sentry for error tracking (optional).

### Data & AI
* **Database:** Supabase (PostgreSQL).
* **Vector Store:** Supabase `pgvector` extension (with HNSW or IVFFlat index).
* **LLM Provider:** OpenAI API (GPT-4o-mini or GPT-3.5-turbo) via LangChain.
* **Embeddings:** OpenAI `text-embedding-3-small` (dimension: 1536).
* **Text Splitting:** LangChain `RecursiveCharacterTextSplitter` (chunk_size=1000, chunk_overlap=200).

---

## 3. Core Features & User Flow

1.  **Content Upload:** User can upload either:
    * **PDF Document:** Full textbooks, papers, lecture notes
    * **Text Summary:** Manually written summaries, notes, or quick reference materials
    
2.  **Ingestion Pipeline (Backend):**
    * User selects/creates a subject.
    * User chooses content type (PDF or Summary).
    
    **For PDFs:**
    * Extract text from PDF (validate file type and size < 10MB).
    * **Chapter Detection (Optional but recommended):**
      - Use regex patterns to detect chapter headers ("Chapter 1", "Section 1.1", etc.)
      - Or allow manual chapter definition by user after upload
      - Create chapter records with page ranges
    * Split text into chunks using `RecursiveCharacterTextSplitter` (chunk_size=1000, chunk_overlap=200).
    * Enrich chunk metadata: `{"page": 5, "chapter_id": "uuid", "chapter_name": "Chapter 1", "subject_id": "uuid", "document_name": "...", "document_type": "pdf"}`
    
    **For Summaries:**
    * Store full text in `documents.content_text` field.
    * Split text into chunks (no page numbers needed).
    * Enrich chunk metadata: `{"subject_id": "uuid", "document_name": "Summary: ...", "document_type": "summary"}`
    * Optionally allow users to associate summaries with specific chapters.
    
    **Common Processing:**
    * Generate embeddings for chunks using OpenAI API.
    * Store chunks and vectors in Supabase with proper indexing.
    * Update document status: 'processing' → 'ready' or 'error'.
3.  **Content Generation (RAG):**
    * User selects scope: **Subject**, **Document** (PDF or Summary), **Chapter**, or **Summary**.
    * User requests content: "Generate 5 flashcards" or "Generate 10 quiz questions".
    * System performs similarity search on selected scope (top_k=5, configurable).
    * Retrieve relevant vector chunks with similarity threshold > 0.7.
    * LLM generates content based *only* on retrieved context.
    * **Use Cases:**
      - Study from entire subject (all PDFs + summaries)
      - Focus on single PDF document
      - Target specific chapter from a PDF
      - Generate questions from a specific summary
    * **CRITICAL:** LLM must return strict JSON format for the frontend to render.
    * Implement fallback behavior when context is insufficient.
    
4.  **Study Mode (Frontend):**
    * Scope selector: Choose what to study (Subject/Document/Chapter/Summary).
    * Interactive UI to flip flashcards with source attribution.
    * Quiz interface with score calculation and explanations.
    * Source citations show: document name, chapter (if applicable), page number (for PDFs).

---

## 4. Database Schema (Supabase)

### Hierarchical Structure: Subject → Documents → Chapters → Chunks

**Table: `subjects`**
* `id` (uuid, PK, default: gen_random_uuid())
* `name` (text, NOT NULL) - e.g., "Computer Networks", "Machine Learning"
* `description` (text)
* `color` (text) - For UI organization (e.g., "#3B82F6")
* `user_id` (uuid, nullable for MVP)
* `created_at` (timestamp with time zone, default: now())
* `updated_at` (timestamp with time zone, default: now())

**Table: `documents`**
* `id` (uuid, PK, default: gen_random_uuid())
* `subject_id` (uuid, fk -> subjects.id ON DELETE CASCADE)
* `document_type` (enum: 'pdf', 'summary', default: 'pdf')
* `filename` (text, NOT NULL)
* `file_size` (bigint, NOT NULL)
* `status` (enum: 'processing', 'ready', 'error', default: 'processing')
* `total_pages` (int, nullable for summaries)
* `content_text` (text, nullable) - For summaries: stores the full text directly
* `user_id` (uuid, nullable for MVP, add FK later for multi-user support)
* `created_at` (timestamp with time zone, default: now())
* `updated_at` (timestamp with time zone, default: now())

**Table: `chapters` (Optional but recommended for better organization)**
* `id` (uuid, PK, default: gen_random_uuid())
* `document_id` (uuid, fk -> documents.id ON DELETE CASCADE)
* `name` (text, NOT NULL) - e.g., "Chapter 1: Introduction"
* `start_page` (int)
* `end_page` (int)
* `order_index` (int) - For sorting chapters
* `created_at` (timestamp with time zone, default: now())

**Table: `document_chunks` (Vector Store)**
* `id` (uuid, PK, default: gen_random_uuid())
* `document_id` (uuid, fk -> documents.id ON DELETE CASCADE)
* `chapter_id` (uuid, fk -> chapters.id ON DELETE SET NULL, nullable)
* `content` (text, NOT NULL)
* `embedding` (vector(1536), NOT NULL)
* `metadata` (jsonb) - Store: {"page": 5, "section": "1.2", "subject_id": "uuid", "chapter_name": "..."}
* `created_at` (timestamp with time zone, default: now())

**Indexes:**
* `idx_documents_subject_id` ON `documents(subject_id)` (btree)
* `idx_chapters_document_id` ON `chapters(document_id)` (btree)
* `idx_document_chunks_document_id` ON `document_chunks(document_id)` (btree)
* `idx_document_chunks_chapter_id` ON `document_chunks(chapter_id)` (btree)
* `idx_document_chunks_embedding` ON `document_chunks` USING ivfflat(embedding vector_cosine_ops) - For vector similarity search
* `idx_document_chunks_metadata` ON `document_chunks` USING gin(metadata) - For filtering by metadata

**Table: `generated_content`**
* `id` (uuid, PK, default: gen_random_uuid())
* `document_id` (uuid, fk -> documents.id ON DELETE CASCADE, nullable)
* `chapter_id` (uuid, fk -> chapters.id ON DELETE CASCADE, nullable)
* `subject_id` (uuid, fk -> subjects.id ON DELETE CASCADE, nullable)
* `scope` (enum: 'subject', 'document', 'chapter') - What level was this generated for?
* `type` (enum: 'flashcard', 'quiz')
* `content_json` (jsonb, NOT NULL) - Stores the questions/answers generated by AI
* `created_at` (timestamp with time zone, default: now())

**Notes:** 
* At least one of `document_id`, `chapter_id`, or `subject_id` must be NOT NULL (check constraint)
* `document_id` can reference either PDF documents or summary documents
* `scope='document'` applies to both PDFs and summaries (differentiated by `documents.document_type`)

---

## 5. PDF Parsing Pipeline (Detailed)

### Recommended Approach: PyMuPDF (Primary) + Unstructured (Fallback)

**Pipeline Steps (10-25 seconds for 50-page PDF):**

1. **File Validation** (< 1s)
   * Check file size (max 10MB)
   * Verify PDF format (MIME type)
   * Scan for corruption

2. **Metadata Extraction** (< 1s)
   ```python
   # Using PyMuPDF
   doc = fitz.open(file_path)
   total_pages = len(doc)
   metadata = doc.metadata  # title, author, creation_date
   ```

3. **Text Extraction** (1-5s for 50 pages)
   ```python
   # Page-by-page with PyMuPDF
   for page_num in range(len(doc)):
       page = doc[page_num]
       text = page.get_text("text")  # preserves layout
       # Store: {page_num, text, char_count}
   ```

4. **Chapter Detection** (< 1s)
   ```python
   # Regex patterns for common chapter formats
   patterns = [
       r'^Chapter\s+(\d+|[IVXLC]+)[:\s]+(.+)$',
       r'^Section\s+(\d+\.\d+)[:\s]+(.+)$',
       r'^\d+\.\s+([A-Z][^.]+)$'
   ]
   # Detect boundaries, create chapter records
   ```

5. **Smart Chunking** (1-2s)
   ```python
   # LangChain RecursiveCharacterTextSplitter
   splitter = RecursiveCharacterTextSplitter(
       chunk_size=1000,
       chunk_overlap=200,
       separators=["\n\n", "\n", ". ", " "]
   )
   # Preserve metadata: page, chapter_id, subject_id
   ```

6. **Batch Embedding Generation** (5-15s)
   ```python
   # OpenAI API in batches of 100
   response = openai.embeddings.create(
       model="text-embedding-3-small",
       input=chunk_texts
   )
   # Rate limiting: 1 second between batches
   ```

7. **Vector Storage** (1-2s)
   ```python
   # Store in Supabase pgvector
   INSERT INTO document_chunks (content, embedding, metadata)
   # Metadata includes: page, chapter_id, subject_id, document_type
   ```

### Error Handling Strategy:

**Quality Check:**
```python
avg_chars = total_chars / total_pages
if avg_chars < 100:
    # Likely scanned/image PDF → fallback to Unstructured with OCR
    use_unstructured_with_ocr(file_path)
```

**Fallback Hierarchy:**
1. PyMuPDF (fast, 90% of cases)
2. Unstructured with Tesseract OCR (scanned PDFs)
3. Return error if both fail

**Common Failure Modes:**
* Corrupted PDF → Return 400 error immediately
* Scanned PDF (no text layer) → Auto-switch to OCR
* Password-protected → Return 400 with clear message
* Extremely complex layout → May need manual chapter definition

---

## 6. API Specification

### REST Endpoints

**Subjects:**
* `POST /api/subjects` - Create a new subject
  * Request: `{"name": "Machine Learning", "description": "...", "color": "#3B82F6"}`
  * Response: `{"id": "uuid", "name": "...", "created_at": "..."}`
  
* `GET /api/subjects` - List all subjects
  * Response: `[{"id": "uuid", "name": "...", "document_count": 5, "created_at": "..."}]`
  
* `GET /api/subjects/{id}` - Get subject with all documents
  * Response: `{"id": "uuid", "name": "...", "documents": [{...}]}`
  
* `PUT /api/subjects/{id}` - Update subject
  * Request: `{"name": "...", "description": "...", "color": "..."}`
  
* `DELETE /api/subjects/{id}` - Delete subject (cascades to all documents)
  * Response: `{"message": "Subject and all documents deleted"}`

**Documents:**
* `POST /api/documents/upload` - Upload PDF file to a subject
  * Request: multipart/form-data with `file` + `subject_id` + `document_type=pdf`
  * Response: `{"document_id": "uuid", "status": "processing", "subject_id": "uuid", "document_type": "pdf"}`
  * Validation: Max 10MB, only PDF files
  
* `POST /api/documents/summary` - Create a text summary document
  * Request: `{"subject_id": "uuid", "title": "Chapter 1 Summary", "content": "Full summary text here...", "chapter_id": "uuid" (optional)}`
  * Response: `{"document_id": "uuid", "status": "processing", "subject_id": "uuid", "document_type": "summary"}`
  * Validation: Max 50KB text, minimum 100 characters
  
* `GET /api/documents` - List all documents (optionally filter by subject or type)
  * Query params: `?subject_id=uuid&document_type=pdf|summary` (both optional)
  * Response: `[{"id": "uuid", "filename": "...", "document_type": "pdf|summary", "subject_name": "...", "status": "ready", "created_at": "..."}]`
  
* `GET /api/documents/{id}` - Get document details
  * For PDFs: Returns with chapters array
  * For summaries: Returns with content_text and associated chapter (if any)
  * Response: `{"id": "uuid", "document_type": "pdf|summary", "filename": "...", "status": "ready", "chapters": [{...}] (if PDF), "content_text": "..." (if summary)}`
  
* `GET /api/documents/{id}/status` - Check processing status
  * Response: `{"status": "processing|ready|error", "progress": 75}`
  
* `DELETE /api/documents/{id}` - Delete document and all related data
  * Response: `{"message": "Document deleted successfully"}`

**Chapters:**
* `POST /api/documents/{document_id}/chapters` - Create/define chapters (manual or auto-detected)
  * Request: `{"name": "Chapter 1: Introduction", "start_page": 1, "end_page": 15}`
  * Response: `{"id": "uuid", "name": "...", "document_id": "uuid"}`
  
* `GET /api/documents/{document_id}/chapters` - List all chapters for a document
  * Response: `[{"id": "uuid", "name": "Chapter 1", "start_page": 1, "end_page": 15}]`
  
* `PUT /api/chapters/{id}` - Update chapter info
  * Request: `{"name": "...", "start_page": 1, "end_page": 15}`
  
* `DELETE /api/chapters/{id}` - Delete chapter (chunks remain linked to document)
  * Response: `{"message": "Chapter deleted"}`

**Content Generation (Scoped by Subject/Document/Chapter/Summary):**
* `POST /api/generate/flashcards` - Generate flashcards using RAG
  * Request: `{"scope": "subject|document|chapter|summary", "scope_id": "uuid", "count": 5, "query": "Focus on neural networks" (optional)}`
  * Examples:
    - Generate from entire subject: `{"scope": "subject", "scope_id": "subject_uuid", "count": 10}` (includes all PDFs + summaries)
    - Generate from specific PDF document: `{"scope": "document", "scope_id": "doc_uuid", "count": 5}`
    - Generate from single chapter: `{"scope": "chapter", "scope_id": "chapter_uuid", "count": 5}`
    - Generate from a summary: `{"scope": "document", "scope_id": "summary_doc_uuid", "count": 5}`
  * Response: `{"flashcards": [{"front": "...", "back": "..."}], "sources": [{"document": "...", "document_type": "pdf|summary", "page": 5, "chapter": "..."}]}`
  
* `POST /api/generate/quiz` - Generate quiz questions (same scoping)
  * Request: `{"scope": "subject|document|chapter|summary", "scope_id": "uuid", "count": 5, "difficulty": "easy|medium|hard" (optional)}`
  * Response: `{"questions": [{"question": "...", "options": [], "correct_answer": 0, "explanation": "...", "source": {"document": "...", "document_type": "pdf|summary", "page": 5}}]}`

**Retrieval Logic Based on Scope:**
- `scope=chapter`: Retrieve chunks where `chapter_id = scope_id`
- `scope=document`: Retrieve chunks where `document_id = scope_id` (works for both PDFs and summaries)
- `scope=subject`: Retrieve chunks where `metadata->>'subject_id' = scope_id` (from all PDFs and summaries in subject)
- **Note:** Summaries are treated as documents with `document_type='summary'`

**Error Response Format (Consistent across all endpoints):**
```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "details": {} // Optional additional context
}
```

**Security & Rate Limiting:**
* CORS: Allow frontend origin only
* Rate limiting: 10 requests/minute per IP for generation endpoints
* File upload: Validate MIME type, scan for malicious content
* API key rotation strategy for OpenAI

---

## 6. Coding Standards & Requirements

### General
* **Modular Code:** Separate logic from UI (Frontend) and Business Logic from Routes (Backend).
* **Environment Variables:** Never hardcode API keys. Use `.env`.
* **Typing:** Strict typing in TypeScript and Type Hints in Python.

### Backend Specifics (Python)
* Use **Dependency Injection** for database sessions.
* Use **Pydantic** for all Request/Response schemas.
* Structure:
    ```text
    /app
      /api (endpoints)
      /core (config, security)
      /services (rag_logic, pdf_parser)
      /models (database models)
      /schemas (pydantic models)
    ```

### Frontend Specifics (Next.js)
* Use **Server Components** where possible, Client Components for interactivity.
* Create reusable UI components (e.g., `<Flashcard />`, `<FileUpload />`).
* Handle "Loading" and "Error" states gracefully in the UI.

---

## 7. Prompt Engineering Strategy (For the LLM)

When generating content, the backend must use a system prompt that enforces JSON output.

### Flashcard Generation Prompt Template:
```python
FLASHCARD_SYSTEM_PROMPT = """You are an educational content generator specialized in creating study flashcards.

CONTEXT FROM DOCUMENT:
{context}

INSTRUCTIONS:
- Generate exactly {count} flashcards based ONLY on the context above
- Each flashcard must test one specific concept from the material
- Questions should be clear and concise
- Answers must be directly supported by the context
- Use simple, student-friendly language

OUTPUT FORMAT (strict JSON, no markdown):
[{{"front": "Question text here", "back": "Answer text here"}}]

Rules:
- Return ONLY the JSON array, no additional text
- Do not use markdown code blocks
- Ensure valid JSON syntax
- If context is insufficient, return fewer flashcards
"""
```

### Quiz Generation Prompt Template:
```python
QUIZ_SYSTEM_PROMPT = """You are an educational assessment creator.

CONTEXT FROM DOCUMENT:
{context}

INSTRUCTIONS:
- Generate exactly {count} multiple-choice questions based ONLY on the context
- Each question must have 4 options (A, B, C, D)
- Only one correct answer per question
- Include a brief explanation for the correct answer
- Difficulty: {difficulty} (easy/medium/hard)

OUTPUT FORMAT (strict JSON, no markdown):
[{{
  "question": "Question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,
  "explanation": "Why this answer is correct"
}}]

Rules:
- correct_answer is the index (0-3) of the correct option
- All content must be verifiable from the context
- Return ONLY valid JSON, no markdown or extra text
"""
```

### Context Handling for Different Document Types:
* **PDFs:** Include page references in retrieved chunks for precise citations
* **Summaries:** No page numbers; use document title and section (if available) for attribution
* **Mixed Scope (Subject-level):** Retrieved chunks may come from both PDFs and summaries - ensure prompts handle both types gracefully

### Fallback Behavior:
* If similarity score < 0.7 for all chunks: Return error "Insufficient context for topic"
* If LLM returns invalid JSON: Retry once with stricter prompt, then return error
* If LLM hallucinates (content not in context): Implement fact-checking layer (optional for Phase 2)
* For summaries: Lower similarity threshold to 0.6 (summaries are typically more concise and may have lower embedding similarity)

---

## 8. Non-Functional Requirements

### Performance Targets:
* PDF processing: < 30 seconds for 50-page document
* Flashcard generation: < 5 seconds for 5 flashcards
* Vector similarity search: < 500ms
* Frontend initial load: < 2 seconds

### Scalability (for TFM justification):
* Support 100 concurrent users
* Handle documents up to 200 pages
* Store up to 10,000 document chunks efficiently
* Horizontal scaling via stateless API design

### Error Handling:
* All API endpoints return consistent error format (see Section 5)
* Graceful degradation when OpenAI API is unavailable
* Retry logic with exponential backoff for transient failures
* User-friendly error messages in the frontend

### Testing Strategy:
* **Unit Tests:** All service functions (pdf_parser, rag_logic)
* **Integration Tests:** RAG pipeline end-to-end
* **API Tests:** All endpoints with various inputs
* **Frontend Tests:** Component rendering and user interactions
* Target: 80% code coverage

### Logging & Monitoring:
* Structured logging with JSON format
* Request ID tracking across all services
* Log levels: DEBUG (development), INFO (production)
* Track: API latency, OpenAI API costs, error rates
* Optional: Sentry for production error tracking

### Security:
* Environment variables for all secrets
* Input validation on all endpoints
* SQL injection prevention via parameterized queries
* XSS protection in frontend
* HTTPS only in production

---

## 9. Implementation Roadmap (Step-by-Step for the AI)

**Phase 1: Backend & Ingestion**
1.  Set up FastAPI with Supabase connection.
2.  Create database tables for subjects, documents (with `document_type` and `content_text` fields), chapters, chunks (see Section 4).
3.  Create the `POST /api/subjects` endpoint for subject management.
4.  Create the `POST /api/documents/upload` endpoint (for PDFs):
    * Parse PDF and extract text with page numbers
    * Implement chapter detection (regex patterns for "Chapter X", "Section X.X")
    * Split into chunks with metadata enrichment (include `document_type: 'pdf'`)
    * Store vectors in `pgvector`
5.  Create the `POST /api/documents/summary` endpoint (for text summaries):
    * Validate text input (min 100 chars, max 50KB)
    * Store full text in `documents.content_text`
    * Split into chunks with metadata enrichment (include `document_type: 'summary'`)
    * Generate embeddings and store in `pgvector`
6.  Create chapter management endpoints (`POST/GET/PUT/DELETE /api/chapters`).

**Phase 2: RAG & Generation**
3.  Implement vector similarity search with pgvector.
4.  Create the `POST /api/generate/flashcards` endpoint using LangChain.
5.  Implement the `POST /api/generate/quiz` endpoint.
6.  Add strict JSON parsing and validation of LLM responses.
7.  Implement error handling and fallback logic.

**Phase 3: Frontend MVP**
8.  Set up Next.js with Shadcn/ui and Tailwind CSS.
9.  Create Subject Management UI:
    * Subject list/grid with color-coded cards
    * Create/edit/delete subject modals
10. Create Content Upload UI with tabs:
    * **PDF Upload Tab:** File selection, subject dropdown, progress tracking
    * **Summary Creation Tab:** Rich text editor or textarea, subject dropdown, optional chapter association
    * Both show processing status and success/error states
11. Create the Dashboard with hierarchical navigation:
    * Subject → Documents (PDFs and Summaries with visual differentiation)
    * For PDFs: Show chapters
    * For Summaries: Show preview of content
    * Breadcrumb navigation
    * Document status indicators
    * Filter by document type (All/PDFs/Summaries)
12. Add document and chapter management (view, edit, delete for both PDFs and summaries).

**Phase 4: Study Interface**
13. Build scope selector with clear visual hierarchy:
    * Study Entire Subject (all PDFs + summaries)
    * Study Single PDF Document
    * Study Specific Chapter (from a PDF)
    * Study from Summary
14. Build the Flashcard Carousel component:
    * Flip animation
    * Show source attribution:
      - For PDFs: "Source: [Document Name], Chapter X, Page Y"
      - For summaries: "Source: [Summary Title]"
    * Progress indicator (X of Y cards)
15. Build the Quiz interface:
    * Score calculation with percentage
    * Show explanations with source citations
    * Filter by difficulty (easy/medium/hard)
    * Display source for each question
16. Connect Frontend to Backend API with scoped generation (handle all 4 scopes).
17. Add loading states, error handling, and prominent source citations.

**Phase 5: Polish & Testing**
16. Write unit tests for backend services.
17. Write integration tests for RAG pipeline.
18. Add error boundaries and user-friendly error messages.
19. Performance optimization (caching, lazy loading).
20. Documentation and deployment setup.

---

## Instructions for the AI Agent:

Please start by setting up the **Backend Project Structure (Phase 1)**. 
1. Define the directory structure following the specification in Section 6.
2. Write the `requirements.txt` with all dependencies (FastAPI, LangChain, Supabase, OpenAI, etc.).
3. Create the `main.py` entry point with FastAPI app initialization and CORS configuration.
4. Create the Supabase connection logic in `/app/core/database.py`.
5. Set up environment variable management in `/app/core/config.py`.
6. Create Pydantic schemas for all API requests/responses.
7. Implement basic error handling middleware.

**When implementing, ensure:**
- All code follows type hints and is well-documented
- Environment variables are never hardcoded
- Database connections use dependency injection
- All endpoints follow the API specification in Section 5
- Error responses follow the consistent format defined
- Logging is implemented with request IDs
- Chapter detection uses common patterns: `r'Chapter\s+(\d+|[IVXLC]+)[:\s]+'`, `r'Section\s+\d+\.\d+'`
- Metadata in chunks always includes:
  * `subject_id` for cross-document RAG queries
  * `document_type` ('pdf' or 'summary') for proper source attribution
  * `page` (for PDFs only, null for summaries)
  * `chapter_name` (when applicable)
- Summaries and PDFs are processed identically after text extraction (same chunking, embedding, storage)

**RAG Configuration to use:**
- chunk_size: 1000
- chunk_overlap: 200
- top_k: 5 (for similarity search)
- similarity_threshold: 0.7
- embedding_model: "text-embedding-3-small"
- llm_model: "gpt-4o-mini" (or "gpt-3.5-turbo" for cost efficiency)