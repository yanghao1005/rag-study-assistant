# backend_v3 tests

This folder is organized for fast, stage-based debugging and validation.

## Structure

- `unit/`: fast tests for isolated functions/services
- `integration/`: pipeline component integration tests
- `e2e/`: full API or full workflow tests
- `fixtures/`: sample PDFs, summaries, and expected outputs

## Quick start

1. Activate your environment.
2. Run all tests:

```bash
pytest -q
```

3. Run by layer:

```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/e2e -q
```

## Recommended first tests

- unit parser smoke
- unit chunker boundaries
- integration retrieval scope filters
- integration JSON output validation + retry
