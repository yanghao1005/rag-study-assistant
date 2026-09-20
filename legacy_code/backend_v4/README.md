# backend_v4

Planning-first specification for the next backend version of the RAG Study Assistant.

Status: documentation + scaffold phase.

## Purpose

This folder defines the objective, scope, architecture, and delivery plan for backend_v4 before any coding starts.

## Documents

- OBJECTIVE.md: project objective, success criteria, and non-goals.
- ARCHITECTURE.md: target architecture and core components.
- API_CONTRACTS.md: frontend-aligned endpoint and payload contracts.
- IMPLEMENTATION_PLAN.md: execution phases and technical tasks.
- MILESTONES.md: timeline checkpoints and acceptance gates.
- RISKS_AND_METRICS.md: risks, mitigations, and KPI targets.
- TASK_CHECKLIST.md: immediate execution checklist for implementation.

## Scaffold

The initial backend_v4 skeleton is now created with architecture-aligned layers:

- app/main.py
- app/core
- app/presentation/api/routes
- app/application/use_cases
- app/domain/models and app/domain/ports
- app/infrastructure/repositories, app/infrastructure/providers, app/infrastructure/parsing
- tests/unit, tests/integration, tests/e2e
- tools

## Strategic Direction

backend_v4 focuses on a production-ready Hybrid RAG baseline with optional Agentic/GraphRAG capabilities behind feature flags.

## Provider Switching and Supabase

The backend now supports configuration-driven adapter selection.

- `VECTOR_REPOSITORY_PROVIDER=memory|supabase`
- `LLM_PROVIDER=openai|stub`
- `EMBEDDINGS_PROVIDER=openai|stub`

To use Supabase as the primary database backend:

1. Copy `.env.example` to `.env`.
2. Set `VECTOR_REPOSITORY_PROVIDER=supabase`.
3. Fill `SUPABASE_URL` and either `SUPABASE_SERVICE_KEY` (recommended) or `SUPABASE_KEY`.
4. Optionally customize `SUPABASE_GENERATED_TABLE` and `SUPABASE_CHUNKS_TABLE`.

If Supabase credentials are missing, the service falls back to the in-memory repository so local development can still run.

For real model providers, set:

- `OPENAI_API_KEY`
- Optional: `OPENAI_BASE_URL`
- Optional: `OPENAI_LLM_MODEL`
- Optional: `OPENAI_EMBEDDING_MODEL`

If OpenAI is selected but key/dependency is missing, backend_v4 falls back to stub providers to keep local tests runnable.

## Pipeline Process Checks

`POST /api/pipeline/run` performs a validation check for each executed stage and returns check diagnostics in `stage_results[].details.checks`.
This allows debugging stage-by-stage and verifying that each process passed before moving to the next one.

## Operational Tools

- `tools/run_pipeline.py`
	- Calls `/api/pipeline/run` with stage/range options.
	- Returns `run_id`, per-stage checks, and artifact paths.

- `tools/benchmark_generation.py`
	- Calls generation endpoint repeatedly and records latency distribution.
	- Computes and stores `p50_ms` and `p95_ms` in JSON reports under `BENCHMARK_REPORTS_DIR`.

## Relationship With Previous Versions

- backend: initial baseline and experimentation.
- backend_v2: refactoring and architecture separation work.
- backend_v3: debug-first production skeleton with Supabase integration.
- backend_v4: thesis blueprint and high-level target direction.
- backend_v4: executable planning package that converts blueprint ideas into build-ready specifications.
