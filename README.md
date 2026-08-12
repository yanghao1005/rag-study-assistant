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
pnpm build
```

Auth notes:
- Email/password + Google OAuth (`Continuar con Google`) — enable Google in Supabase Auth providers.
- Password reset: `/forgot-password` → email link → `/reset-password`.
- Add redirect URLs in Supabase: `http://localhost:3000/auth/callback` (and prod URL).

Optional retrieval rerank (backend `.env`):

```bash
RERANK_PROVIDER=llm
```

## Flujo mínimo

1. Crear cuenta en `/login`
2. Crear asignatura
3. Subir PDF → esperar estado **Listo**
4. Chat / Flashcards / Quiz

## Rama de despliegue

La rama de producción / entornos reales es **`main`**.
