# frontend_v2

Modern Next.js + shadcn-style frontend scaffold for backend_v5.

## Run

```bash
pnpm install
pnpm dev
```

Open http://localhost:3000

First-time setup redirects protected routes to `/onboarding` for Supabase sign-in.

## Backend URL

Set this environment variable if backend is not running at default:

```bash
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000/api
```

Default fallback in code is `http://localhost:8000/api`.

## Supabase Auth Environment Variables

Set these in `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=your_project_url
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your_publishable_key
```

## Current Implemented Vertical Slice

- Upload document (`/documents/new`)
- Poll ingestion job status
- Generate flashcards (`/generate`)
- Generate quiz (`/generate`)
- Ask chat (`/chat`)
- View generation history (`/history`)

## Required Inputs in Toolbar

- Subject (loaded from authenticated user scope)
- Document ID (set automatically after upload, can be edited)

## Reserved Future Modules (UI slots already present)

- Analytics
- Knowledge Graph
- Planner
- Admin

These pages are present as reserved placeholders to avoid shell redesign later.
