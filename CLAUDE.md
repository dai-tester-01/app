# LiteLLM Model Comparator

## Purpose

This is a compact school project that compares responses from multiple LLMs through LiteLLM.
The browser UI submits one prompt, sends it to all configured models concurrently, and shows
responses, latency, token usage, estimated cost, provider errors, and optional judge scores.

## Stack

- Python 3.11+
- FastAPI with Jinja templates and HTMX
- LiteLLM for provider-agnostic model calls
- Pydantic Settings for environment-based configuration
- Poetry for dependencies
- Ruff, mypy, and pytest for quality checks

## Repository layout

```text
src/model_comparator/
  config.py    # Environment-backed Settings
  main.py      # FastAPI routes and application lifecycle
  models.py    # Pydantic response models
  service.py   # Concurrent LiteLLM comparison and optional judging
templates/     # Jinja page and HTMX result fragment
static/        # Minimal frontend CSS
tests/         # Mocked unit and endpoint tests
```

## Key behavior

- `ComparisonService.compare()` starts all configured model calls with `asyncio.gather`.
- A failure from one provider is represented on that model's result; it must not fail the whole
  comparison.
- `JUDGE_MODEL` is optional. When configured, it evaluates only successful model responses.
- Provider credentials are never stored in source control. LiteLLM reads them from environment
  variables such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GEMINI_API_KEY`.

## Local commands

```bash
cp .env.example .env
poetry install
poetry run uvicorn model_comparator.main:app --reload
poetry run ruff format --check .
poetry run ruff check .
poetry run mypy
poetry run pytest
```

## Agent guidance

- Keep the project intentionally small; avoid adding databases, authentication, queues, or
  frontend frameworks unless explicitly requested.
- Put provider orchestration in `service.py`; keep HTTP handlers in `main.py` thin.
- Update `.env.example` and `README.md` for every new setting.
- Add deterministic tests for behavior changes and mock `model_comparator.service.acompletion`;
  tests must not call external providers.
- Do not commit `.env`, API keys, or prompt/response data that could contain sensitive content.
