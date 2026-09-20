# backend_v4 Objective

## Vision

Deliver a reliable and testable backend that supports study workflows (summary, flashcards, quiz) with high factual grounding, predictable latency, and clear observability.

## Primary Objective

Build backend_v4 as a modular FastAPI system that combines:

- deterministic Hybrid RAG for default operations,
- Summary-aware retrieval for chapter/global questions,
- optional Agentic and GraphRAG enhancements behind feature flags.

## Problem Statement

Current RAG flows can fail in three common ways:

- weak retrieval relevance for broad conceptual questions,
- hallucinated or low-quality educational outputs,
- difficult debugging when processing and generation are tightly coupled.

backend_v4 addresses these by standardizing retrieval strategy, output validation, and stage-level diagnostics.

## Success Criteria

1. Retrieval quality

- At least 85% top-5 relevance on internal benchmark queries.
- Clear source attribution for generated flashcards and quiz items.

1. Reliability

- 100% schema-valid JSON responses for structured endpoints.
- Automatic retry-on-parse-failure with deterministic fallback error.

1. Performance

- p95 generation latency below 8 seconds on thesis benchmark workload.
- Ingestion pipeline supports asynchronous processing with progress status.

1. Maintainability

- Layered architecture (domain/application/infrastructure/presentation).
- Stage-selectable pipeline execution and debug artifacts for every run.

## Scope (In)

- PDF and summary ingestion.
- Semantic chunking and metadata-rich indexing.
- Hybrid retrieval (vector + lexical + rerank).
- Summary generation, flashcard generation, quiz generation.
- Structured logging, tracing, and benchmark instrumentation.

## Non-Goals (Initial)

- Full autonomous multi-agent orchestration in default mode.
- Multi-tenant billing and usage monetization features.
- Real-time collaborative editing.

## Design Principles

- Deterministic by default; agentic by exception.
- Strict contracts between pipeline stages.
- Observable first: every critical decision is traceable.
- Safety first: grounded responses with explicit uncertainty when context is weak.
