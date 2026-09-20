# Frontend v2 Implementation Blueprint

## 1. Objective

Build a new `frontend_v2` using Next.js App Router + shadcn/ui for `backend_v5`, with:

- modern and intentional UI design
- scalable architecture for future modules
- maintainable codebase with strict boundaries
- extension-ready layout so new features can be integrated without redesigning core navigation or shell

This document is phase 1 (design + architecture) before full implementation.

## 2. Product Scope (Current + Future-Ready)

### 2.1 Current backend_v5-aligned features (must ship first)

- authentication-aware app shell
- subject/document workspace
- upload document flow
- ingestion job status tracking
- generate flashcards
- generate quiz
- ask chat question
- generated history view

### 2.2 Future-reserved feature zones (not implemented now, but designed in UI)

- analytics and learning insights panel
- graph knowledge view (triplets, concept map)
- collaborative study room / shared sessions
- scheduled review planner and reminders
- model/configuration center (retrieval + generation tuning)
- admin observability workspace (jobs, costs, quality metrics)

The shell and information architecture will include these zones as disabled or "Coming Soon" entries from day one.

## 3. Backend Contract Alignment (backend_v5)

### 3.1 Required endpoints for MVP

- `POST /api/documents/upload`
- `POST /api/documents/summary`
- `GET /api/jobs/{job_id}`
- `POST /api/generate/flashcards`
- `POST /api/generate/quiz`
- `POST /api/generate/summary`
- `GET /api/generate/history`
- `POST /api/chat/ask`

### 3.2 Frontend contract principles

- never send user identity from UI as source of truth
- use bearer token auth on all protected requests
- use typed request/response clients generated from shared TS schemas
- all API access goes through `src/lib/api/*`, never directly in components

## 4. Tech Stack

- Next.js (App Router, React Server Components where useful)
- TypeScript strict mode
- shadcn/ui + Radix primitives
- Tailwind CSS v4 + CSS variables
- TanStack Query for server state
- Zustand only for local UI/session state (minimal)
- React Hook Form + Zod for forms
- Sonner for toast notifications
- date-fns for date formatting

## 5. Architecture for Scalability

### 5.1 Folder strategy (feature-oriented)

```text
frontend_v2/
  IMPLEMENTATION.md
  src/
    app/
      (marketing)/
      (auth)/
      (workspace)/
        layout.tsx
        dashboard/page.tsx
        subjects/[subjectId]/page.tsx
        documents/[documentId]/page.tsx
        generate/page.tsx
        chat/page.tsx
        history/page.tsx
        analytics/page.tsx         # reserved
        graph/page.tsx             # reserved
        planner/page.tsx           # reserved
        admin/page.tsx             # reserved
    components/
      ui/                          # shadcn components
      shell/
      documents/
      generation/
      chat/
      history/
      placeholders/                # coming soon cards/sections
    features/
      auth/
      documents/
      jobs/
      generation/
      chat/
      history/
      analytics/                   # reserved contracts
      graph/                       # reserved contracts
    lib/
      api/
      schemas/
      query/
      utils/
      constants/
    styles/
      tokens.css
```

### 5.2 Boundaries

- `app/*` defines route composition only
- `features/*` contains domain logic + hooks + service calls
- `components/*` contains presentational reusable UI
- `lib/api/*` contains typed HTTP clients and mappers

No route should call fetch directly if a feature client exists.

## 6. Modern Visual Direction

### 6.1 Design language

Direction: "Editorial Productivity Lab"

- strong typography hierarchy
- high contrast neutral base with electric accent
- spacious rhythm, card layering, subtle gradient atmosphere
- focused motion for state transitions and progressive disclosure

### 6.2 Typography

- Headings: `Space Grotesk`
- Body/UI: `Manrope`
- Monospace snippets: `JetBrains Mono`

### 6.3 Color strategy (CSS variables)

- primary background: warm-light neutral
- panel background: elevated neutral card
- accent: cyan/teal spectrum for actionable states
- warning: amber
- destructive: rose-red

No hardcoded utility colors in components; use semantic tokens only.

### 6.4 Motion

- page-enter transition: 180-240ms fade + translate
- list stagger for generation/history cards
- skeleton-to-content morph on loaded data
- no excessive micro-animation noise

## 7. Core UI Composition

### 7.1 App shell

- left rail: primary navigation
- top bar: workspace context + global actions + status chips
- main content: split-ready canvas
- right contextual panel: diagnostics, source previews, and future feature drawer

### 7.2 Reserved space strategy (important)

- nav includes reserved routes with feature flags
- dashboard has fixed "Future Modules" zone (cards with stable IDs)
- detail pages include right panel slots for:
  - insights
  - graph context
  - recommendations
- route-level layout keeps these slots even if currently empty

This prevents future feature collisions and major layout rewrites.

## 8. Data and State Strategy

### 8.1 Server state

- TanStack Query keys by domain:
  - `jobs.byId(jobId)`
  - `generation.history(scope, scopeId)`
  - `documents.bySubject(subjectId)`
- stale-time tuned per endpoint
- optimistic updates only where safe (history append)

### 8.2 UI state

- local-only store for panel toggles, filter chip state, draft prompts
- never duplicate API source-of-truth in local store

## 9. Implementation Phases

### Phase 0: Foundation

- scaffold Next.js + TypeScript + Tailwind v4
- initialize shadcn and base components
- define tokens and app shell
- configure linting, formatting, import boundaries

### Phase 1: Backend v5 MVP integration

- implement API clients + DTO schemas
- upload + job polling flow
- flashcards/quiz/chat/history pages
- standardized loading/error/empty states

### Phase 2: Future-ready placeholders

- add reserved pages and shell slots
- add feature flags map and guards
- add reusable "Coming Soon" blocks with stable layout contracts

### Phase 3: Quality and hardening

- accessibility pass (keyboard, aria, contrast)
- performance pass (bundle split, dynamic import, suspense)
- component documentation and story examples

## 10. Engineering Standards (Maintainability)

- strict TypeScript, no `any` in feature modules
- route components stay thin; hooks/services contain logic
- shared schema validation for every API payload
- explicit error boundary per route group
- unit tests for critical hooks/services
- e2e smoke path: upload -> job -> generate -> chat -> history

## 11. Future Integration Contracts

Add extension points now:

- `FeatureRegistry` for nav entries + route metadata
- `RightPanelSlot` enum for contextual tools
- `DashboardWidgetContract` with id/title/state/actions
- `ExperimentFlag` registry for incremental rollouts

With these contracts, new features become plug-in modules instead of structural rewrites.

## 12. First Build Backlog (Execution Order)

1. Initialize `frontend_v2` project and tooling.
2. Build design tokens + shell.
3. Implement auth-aware API client and request interceptor.
4. Implement upload + job status timeline.
5. Implement generation pages (flashcards, quiz).
6. Implement chat and history.
7. Add reserved feature routes and placeholder widgets.
8. Run accessibility/performance pass.

## 13. Definition of Done (for frontend_v2 initial release)

- full happy path works with backend_v5 endpoints
- clean architecture boundaries respected
- shadcn-based component system established
- visual design modern and consistent across desktop/mobile
- reserved zones for future modules are visible and stable
- test and lint pipelines pass
