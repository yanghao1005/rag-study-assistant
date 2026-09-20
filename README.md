# Studyraft

Turn your own PDFs into a study loop: **subject → documents → cited chat → flashcards / quiz → spaced review (SM-2)**.

## Layout

| Path | Role |
|------|------|
| `backend/` | FastAPI hexagonal API (ingestion, hybrid RAG, generation, planner) |
| `frontend/` | Next.js 16 app (Studyraft UI) |
| `backend/supabase/migrations/` | Schema, RLS, storage, search (`0001`–`0008`) |
| `legacy_code/` | Archived stacks (reference only) |

## Requirements

- Python 3.12+
- Node 20+ (22 recommended) and pnpm 10
- A Supabase project (Auth, Postgres, Storage, pgvector)
- An OpenAI API key (Gemini is optional for chat)

## Docker

From the repo root, with `backend/.env` filled in and the frontend public vars exported:

```bash
export NEXT_PUBLIC_SUPABASE_URL=...
export NEXT_PUBLIC_SUPABASE_ANON_KEY=...
docker compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/health
- Defense deck: http://localhost:3000/presentacio

Apply migrations `0001`–`0008` on the Supabase project before using the app.

## Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env   # fill Supabase + OpenAI
PYTHONPATH=. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Quality:

```bash
cd backend
python -m pytest tests/unit -q
python -m ruff check app tests
python -m mypy app
# optional (hits live services):
# RUN_REAL_INTEGRATION=1 python -m pytest tests/integration -v
```

Debug helpers:

```bash
python -m app.entrypoints.cli.pipeline --user-id <uid> --document-id <id> --from-stage parse --to-stage store
python -m app.entrypoints.cli.benchmark --user-id <uid> --subject-id <sid> --query "value proposition"
```

## Frontend

```bash
cd frontend
pnpm install
cp .env.example .env.local   # Supabase anon + NEXT_PUBLIC_API_URL
pnpm dev                     # http://localhost:3000
```

Build and checks:

```bash
pnpm exec tsc --noEmit
pnpm test
pnpm build
pnpm exec playwright install chromium
pnpm test:e2e
```

Auth:

- Email/password on `/login` (sign in or create an account)
- Password reset: `/forgot-password` → email link → `/reset-password`
- Add redirect URLs in Supabase: `http://localhost:3000/auth/callback` (and the production URL)

## Retrieval flags (backend `.env`)

Defaults: hybrid search 20 dense + 20 lexical → 8 chunks, LLM rerank off, hierarchical RAG on, agentic RAG off.

```bash
RERANK_PROVIDER=llm
ENABLE_HIERARCHICAL_RAG=true
ENABLE_AGENTIC_RAG=true
ENABLE_DEBUG_ENDPOINTS=true
```

Agentic RAG also needs the toggle in `/settings`. Scanned PDFs fail at parse on purpose (no OCR).

## Minimal flow

1. Create an account at `/login`
2. Create a subject
3. Upload a PDF and wait until status is **Ready** (`Listo` in the Spanish UI)
4. Chat, flashcards, quiz, or review
5. Profile and agentic RAG on `/settings`

The UI is informal Spanish (tú). The API and this README are in English.

## Branch

Production is **`main`**.
