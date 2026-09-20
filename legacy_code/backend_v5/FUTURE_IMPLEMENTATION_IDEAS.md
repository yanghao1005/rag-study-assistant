# backend_v5 Future Implementation Ideas

This document captures high-value ideas beyond flashcards and quizzes.
Use it as the post-TFM product evolution backlog.

## 1. Interactive Tutor Agent

What:

- Conversational study assistant that answers user questions with source citations.

Why:

- Supports follow-up questions and deeper conceptual understanding.

How:

- Add `/api/chat/ask` endpoint.
- Agent uses tools: retrieve_context, summarize_scope, generate_flashcards, generate_quiz.
- Enforce fallback when evidence is weak.

Priority:

- High

## 2. Multi-Style Summaries

What:

- Summary modes: concise, exam-focused, conceptual, chapter-by-chapter, one-page review sheet.

Why:

- Different study tasks require different compression levels.

How:

- Extend summary endpoint with `summary_mode` parameter.
- Reuse summary index and retrieval context builder.

Priority:

- High

## 3. Weak-Topic Adaptive Drills

What:

- Automatically generate practice questions from user mistakes.

Why:

- Personalization increases learning outcomes.

How:

- Track incorrect answers in `study_events` table.
- Build drill generator using weak-topic scores.

Priority:

- High

## 4. Misconception Detector

What:

- Analyze free-text student answers and identify misconceptions.

Why:

- Moves from assessment to targeted remediation.

How:

- Add endpoint for answer analysis.
- Compare student response against retrieved evidence and model rubric.

Priority:

- Medium

## 5. Exam Simulator

What:

- Timed tests with mixed question types and final score report.

Why:

- Simulates real exam pressure and readiness.

How:

- Create exam session model with timer and section weighting.
- Persist responses and post-exam diagnostics.

Priority:

- Medium

## 6. Concept Map Generator

What:

- Build graph of entities and relationships from documents.

Why:

- Helps learners understand structure and dependencies across concepts.

How:

- Optional graph extraction pipeline.
- Return graph JSON for frontend visualization.

Priority:

- Medium

## 7. Compare-and-Contrast Generator

What:

- Generate structured comparisons: concept A vs concept B.

Why:

- Excellent for theory-heavy and exam comparison questions.

How:

- Prompt template and schema for differences, similarities, use cases, pitfalls.

Priority:

- Medium

## 8. Memory Aids and Mnemonics

What:

- Generate mnemonics, analogies, and memory hooks.

Why:

- Improves retention and recall speed.

How:

- New endpoint with style and complexity controls.

Priority:

- Low

## 9. Study Plan and Revision Scheduler

What:

- Personalized weekly study plans and spaced revision schedule.

Why:

- Bridges content generation and practical study execution.

How:

- Inputs: exam date, available time, weak topics.
- Outputs: schedule and reminders.

Priority:

- Medium

## 10. Explain-Why Mode

What:

- For each generated answer, provide concise reasoning grounded in sources.

Why:

- Increases trust and pedagogical value.

How:

- Add optional `explain_why` flag in generation APIs.

Priority:

- High

## Suggested Rollout Order

1. Interactive tutor agent
2. Multi-style summaries
3. Weak-topic adaptive drills
4. Explain-why mode
5. Exam simulator
6. Concept map generator

## Governance Notes

- Keep deterministic generation as baseline for structured outputs.
- Gate agentic workflows with feature flags.
- Add benchmark and grounding checks before enabling features globally.
