# backend_v3

Debug-first and deployable RAG backend skeleton for SmartStudy.

## Features in this implementation slice

- FastAPI app with standardized error format and request IDs.
- Step-selectable pipeline runner (single stage, stage range, full run).
- Debug endpoint: `POST /api/pipeline/run`.
- CLI runner: `python -m tools.pipeline`.
- Test scaffold with smoke/API/pipeline tests.
- Docker and docker-compose for easy deployment.

## Run locally

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/health
```

## Run pipeline from API

```bash
curl -X POST http://localhost:8000/api/pipeline/run \\
  -H "Content-Type: application/json" \\
  -d "{\"document_id\":\"doc-1\",\"document_text\":\"Chapter 1 Intro\\fSection 1.1 Basics\",\"from\":\"parse_document\",\"to\":\"split_chunks\",\"debug\":true}"
```

## Run pipeline from CLI

```bash
python -m tools.pipeline --document-id doc-1 --document-text "Chapter 1 Intro" --stage parse_document --debug
python -m tools.pipeline --document-id doc-1 --document-text "Chapter 1 Intro" --from parse_document --to generate_output
```

## Run tests

```bash
pytest tests -q
```

## Deploy with Docker

```bash
cp .env.example .env
docker compose up --build
```

## Supabase configuration (RLS-safe)

- Set `SUPABASE_URL`, `SUPABASE_KEY`, and `SUPABASE_SERVICE_KEY` in `.env`.
- Default behavior is secure: anon fallback is disabled (`SUPABASE_ALLOW_ANON_FALLBACK=false`).
- Only set `SUPABASE_ALLOW_ANON_FALLBACK=true` for local/non-RLS environments.
