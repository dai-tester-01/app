# LiteLLM Model Comparator

A small FastAPI playground that sends one prompt to several models at the same time through
[LiteLLM](https://docs.litellm.ai/), then displays each response alongside latency, token use,
estimated cost, and optional judge scores.

It is intentionally compact enough for a school project while demonstrating production-minded
practices: typed configuration, isolated provider failures, async concurrency, automated tests,
linting, type checking, CI, Docker, and secret-safe environment configuration.

## How it works

```text
Prompt ──> GPT / Claude / Gemini (concurrently) ──> response + latency + tokens + cost
                                                     └── optional judge scores
```

One provider failing never prevents the other results from appearing. LiteLLM reads provider
credentials from the environment, so the application does not store API keys.

## Quick start

Requirements: Python 3.11+ and [Poetry](https://python-poetry.org/).

```bash
cp .env.example .env
# Add API keys in .env and adjust MODELS to the providers you use.
poetry install
poetry run uvicorn model_comparator.main:app --reload
```

Open <http://localhost:8000>. The default model list contains OpenAI, Anthropic, and Gemini
examples. Configure only models for which you have provider credentials and access.

### Environment variables

| Variable | Purpose |
| --- | --- |
| `MODELS` | Comma-separated LiteLLM model IDs to compare. |
| `JUDGE_MODEL` | Optional LiteLLM model ID used to rate successful responses. |
| `REQUEST_TIMEOUT_SECONDS` | Per-model timeout, default `30`. |
| `MAX_PROMPT_CHARACTERS` | Server-side prompt limit, default `8000`. |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` | Provider keys required by selected models. |

LiteLLM supports many more model providers and identifiers; see its
[provider documentation](https://docs.litellm.ai/docs/providers).

## Docker

```bash
cp .env.example .env
# Fill the required provider keys.
docker compose up --build
```

## Development

```bash
poetry run ruff format --check .
poetry run ruff check .
poetry run mypy
poetry run pytest
```

The tests mock LiteLLM, so they do not make network calls or require API keys. See
[CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.
