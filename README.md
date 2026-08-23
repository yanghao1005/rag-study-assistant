# Studyraft (RAG Study Assistant)

Convierte PDFs propios en un ciclo de estudio: **asignatura → documentos → chat con citas → flashcards / quiz**.

## Estructura

| Carpeta | Rol |
|---------|-----|
| `backend/` | FastAPI hexagonal (RAG, ingestión, generación) |
| `frontend/` | Next.js 16 · Studyraft UI |
| `legacy_code/` | Stacks antiguos (solo referencia) |
| `backend/supabase/migrations/` | SQL de esquema / RLS / búsqueda |

## Requisitos

- Python 3.12+
- Node 20+ (recomendado 22) + pnpm 10
- Proyecto Supabase (Auth + Postgres + Storage + pgvector)
- API key OpenAI (o Gemini según `.env`)

## Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env   # rellena Supabase + OpenAI
# aplica migraciones en Supabase (ver backend/supabase/README.md)
PYTHONPATH=. python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Calidad:

```bash
cd backend
python -m pytest tests/unit -q
python -m ruff check app tests
python -m mypy app
# opcional (credenciales reales):
# $env:RUN_REAL_INTEGRATION=1; python -m pytest tests/integration -v
# pipeline debug:
# python -m app.entrypoints.cli.pipeline --user-id <uid> --document-id <id> --from-stage parse --to-stage store
# python -m app.entrypoints.cli.benchmark --user-id <uid> --subject-id <sid> --query "ATP"
```

## Frontend

```bash
cd frontend
pnpm install
cp .env.example .env.local   # Supabase anon + NEXT_PUBLIC_API_URL
pnpm dev                     # http://localhost:3000
```

Build:

```bash
pnpm exec tsc --noEmit
pnpm test
pnpm build
```

Smoke E2E (Playwright, after `pnpm build`):

```bash
pnpm exec playwright install chromium
pnpm test:e2e
```

Auth notes:
- Email/password on `/login` (entrar / crear cuenta).
- Password reset: `/forgot-password` → email link → `/reset-password`.
- Add redirect URLs in Supabase: `http://localhost:3000/auth/callback` (and prod URL).

Optional retrieval extras (backend `.env`):

```bash
RERANK_PROVIDER=llm
ENABLE_HIERARCHICAL_RAG=true
ENABLE_AGENTIC_RAG=true
ENABLE_DEBUG_ENDPOINTS=true
```

## Docker

Desde la raíz del repo (con `backend/.env` relleno y variables `NEXT_PUBLIC_*` en el entorno):

```bash
docker compose up --build
```

- API: http://localhost:8000/api/docs
- App: http://localhost:3000

Aplica las migraciones `0001`–`0008` en Supabase antes de usarlo.

## Flujo mínimo

1. Crear cuenta en `/login`
2. Crear asignatura
3. Subir PDF → esperar estado **Listo**
4. Chat / Flashcards / Quiz / Repaso
5. Ajustes en `/settings` (nombre, RAG agentic)

## Rama de despliegue

La rama de producción / entornos reales es **`main`**. La memoria LaTeX vive en la rama `docs/tfm-latex` (`docs/tfm/`), no en `main`.
