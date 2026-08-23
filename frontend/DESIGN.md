# Studyraft — Design System & Interface Declaration

> Product UI name: **Studyraft**  
> Repo / formal: RAG Study Assistant  
> Status: binding for Phase 6–7 frontend work  
> Voice: calm, precise, study-first — never “AI dashboard”

---

## 1. Product promise (UX north star)

Studyraft helps a student turn **their own PDFs** into a focused study loop:

**Subject → Documents → Understand (Chat) → Practice (Flashcards / Quiz)**

Every screen answers one question:

| Screen | User question |
|--------|----------------|
| Subjects | ¿Qué estoy estudiando ahora? |
| Documents | ¿Qué material tengo y está listo? |
| Chat | ¿Qué dice *mi* material sobre X? |
| Flashcards | ¿Puedo recordar lo esencial? |
| Quiz | ¿Puedo aplicarlo? |

If a UI element does not serve that loop, it does not ship.

---

## 2. Visual direction — “Nordic Desk”

A quiet study desk under cool daylight. Academic without looking like a newspaper; modern without looking like a SaaS purple template.

### Do
- Cool mist paper backgrounds (blue-gray wash, soft grain)
- Charcoal-blue ink for reading
- One accent: deep teal (trust, focus, growth)
- Large readable type for study content
- Generous whitespace; one primary action per view
- Motion that clarifies hierarchy (enter, focus, status), not decoration

### Don’t
- Purple / indigo gradient themes
- Cream paper + terracotta + display serif “AI brochure” look
- Dense broadsheet / hairline newspaper layouts
- Dark mode as default
- Glow effects, glassmorphism stacks, pill-chip fireworks
- Card grids in heroes / empty brand moments
- Emoji as UI chrome
- Multi-layer drop shadows

### Brand test
On auth / first viewport: remove the nav — the wordmark **Studyraft** must still own the screen. No competing headline louder than the brand.

---

## 3. Color system

Tokens live in CSS variables (`src/styles/globals.css`). Semantic names map to shadcn so components stay portable.

| Token | Role | Notes |
|-------|------|--------|
| `--background` | App canvas | Mist paper, not pure white |
| `--foreground` | Body ink | Near-black blue |
| `--primary` | Main CTA / key actions | Deep teal |
| `--primary-foreground` | Text on primary | Off-white |
| `--muted` / `--muted-foreground` | Secondary surfaces / hints | Cool gray |
| `--accent` | Soft highlight (selected nav, focus wash) | Teal tint, low chroma |
| `--destructive` | Errors / delete | Clear red, sparingly |
| `--border` | Dividers | Hairline cool gray |
| `--ring` | Focus ring | Teal, visible for a11y |
| `--signal-ready` | Document ready | Soft green |
| `--signal-processing` | Ingestion running | Amber |
| `--signal-error` | Failed job | Destructive |

Status colors are **signals**, not decoration. Prefer text + small status mark over colorful badges.

---

## 4. Typography

| Role | Family | Use |
|------|--------|-----|
| Brand / display | **Syne** | Wordmark, page titles (sparingly) |
| UI / body | **Source Sans 3** | Nav, forms, chat, buttons |
| Mono (rare) | system ui-monospace | Citations ids, debug only |

### Scale (desktop)
- Brand mark: ~40–56px / Syne / weight 700
- Page title: 28–32px / Syne 600
- Section: 18–20px / Source Sans 600
- Body: 16px / 1.55 line-height
- Study content (chat answer, card face): 17–18px / 1.6
- Meta / captions: 13–14px / muted

Never use Inter, Roboto, Arial, or bare system UI as the designed stack.

---

## 5. Layout & information architecture

### Auth / entry
Single composition: brand, one short line of purpose, one CTA group (Sign in). Soft atmospheric background. No feature grid, no stats.

### App shell (authenticated)
```
┌──────────┬────────────────────────────────────────┐
│ Brand    │ Subject context          [user]        │
│          ├────────────────────────────────────────┤
│ Subjects │                                        │
│ · Bio    │   ONE primary workspace                │
│ · Law    │   (docs | chat | cards | quiz)         │
│          │                                        │
│ ───────  │                                        │
│ Settings │                                        │
└──────────┴────────────────────────────────────────┘
```

- **Left rail (~240px):** subjects list + create; secondary links at bottom
- **Top context bar:** current subject name + mode tabs (Documents / Chat / Flashcards / Quiz)
- **Main:** one job; no competing side panels unless Chat history (collapsible)

### Mobile
- Subjects become a drawer / full-screen picker
- Mode tabs become a bottom or under-header segmented control
- Chat composer sticky bottom; answers scroll above

### Cards policy
Default: **no cards**. Use cards only when the container *is* the interaction (document row actions, flashcard face, quiz option group). If removing border/shadow/radius doesn’t hurt understanding, remove it.

---

## 6. Interaction principles (user-friendly)

1. **Subject-first** — block study features until a subject exists; onboarding = create first subject + upload first PDF.
2. **Progress is visible** — ingestion shows stage-aware status (`queued → processing → ready`), poll quietly, never make the user guess.
3. **Citations are first-class** — chat answers show numbered sources; click → highlight / scroll to chunk meta (page, document).
4. **Keyboard for practice** — flashcards: Space/Enter flip, ←/→ navigate; quiz: 1–4 select, Enter confirm.
5. **Destructive actions confirm** — delete document / subject requires explicit confirm dialog.
6. **Empty states teach the next step** — one sentence + one primary button (e.g. “Sube un PDF para empezar”).
7. **Errors are actionable** — “No se pudo indexar. Reintentar” not only “Error 500”.
8. **Loading without layout jump** — skeletons match final content shape; prefer `useTransition` / Query `isPending` for soft waits.
9. **Focus & a11y** — visible focus rings; labels on inputs; `aria-live` for ingestion status and quiz feedback.
10. **Density for study** — prefer reading comfort over packing widgets.

### Motion budget (intentional, 2–3 patterns max)
- Page / panel enter: 180–220ms fade + slight Y translate
- Flashcard flip: 280ms rotateY
- Status pulse on processing: subtle opacity breathe (respect `prefers-reduced-motion`)

---

## 7. Screen inventory (Phase 6–7)

| Route | Purpose | Primary CTA |
|-------|---------|-------------|
| `/login` | Auth | Continuar con email / magic link |
| `/onboarding` | First subject | Crear asignatura |
| `/subjects` | Pick / manage subjects | Abrir / Nueva |
| `/subjects/[id]/documents` | Upload + list + status | Subir PDF |
| `/subjects/[id]/chat` | RAG Q&A + citations | Preguntar |
| `/subjects/[id]/flashcards` | Review deck | Generar / Siguiente |
| `/subjects/[id]/quiz` | Practice quiz | Generar / Responder |
| `/design` | Living styleboard (dev) | — |
| `/design/wireframes` | Visual interface mockups (dev) | — |

**Review these mockups before coding Phase 6.** Wireframe behavior is specified in the Cursor canvas `studyraft-ui-spec`.

Streaming chat is optional for v1; if deferred, show a clear pending state then full answer + citations.

---

## 8. Component vocabulary

Build with shadcn **New York** + these product patterns:

| Pattern | Notes |
|---------|--------|
| `AppShell` | Rail + context bar + main |
| `SubjectList` | Active state = left teal bar + muted wash (not a card) |
| `ModeTabs` | Text tabs, underline indicator |
| `DocumentRow` | Filename, status signal, actions on hover/focus |
| `UploadDropzone` | Dashed border, large hit area, keyboard accessible |
| `ChatThread` | User right/muted; assistant full-width reading column |
| `CitationList` | Compact numbered list under answer |
| `FlashcardStage` | Single large face, centered |
| `QuizStage` | One question; options as large selectable rows |
| `EmptyState` | Brand-adjacent illustration optional later; text + CTA first |
| `ConfirmDialog` | Destructive clarity |

---

## 9. Copy tone (ES)

- Tú, claro, corto.
- Prefer “Tu documento está listo” over “Ingesta completada exitosamente”.
- Avoid hype: no “potenciado por IA revolucionaria”.
- Technical terms only when useful (`listo`, `procesando`, `error al indexar`).

---

## 10. Implementation checklist

- [x] Design declaration (this file)
- [x] CSS tokens + Tailwind theme wiring
- [x] Fonts in root layout
- [x] `/design` styleboard
- [x] `/design/wireframes` mockups
- [x] Phase 6: auth + shell + subjects CRUD UI
- [x] Phase 7: documents upload, chat, flashcards, quiz
- [x] Phase 8: polish, mypy, full smoke E2E (Playwright + CI ruff/mypy/vitest)
- [x] Citas clicables con nombre de PDF
- [x] Reintentar ingestión
- [x] Ajustes / perfil
- [x] Quiz Enter confirma
- [x] Docker Compose del stack nuevo
- [x] RAG jerárquico, pipeline debug, agentic (flag), benchmarks, planner

Any new UI PR should pass the brand test, cards policy, and one-job-per-screen rule before merge.
