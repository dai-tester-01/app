# Contributing

## Local setup

1. Install Python 3.11+ and Poetry.
2. Copy `.env.example` to `.env`.
3. Add only the provider credentials needed for your configured models.
4. Install dependencies with `poetry install`.

Never commit `.env`, API keys, copied responses containing sensitive data, or generated local
artifacts.

## Before opening a pull request

Run the same checks enforced by CI:

```bash
poetry run ruff format --check .
poetry run ruff check .
poetry run mypy
poetry run pytest
```

Add or update tests for behavior changes. Tests must mock provider calls: they should be
deterministic, free, and safe to run in CI.

## Code guidelines

- Keep request handling thin; place provider orchestration in `ComparisonService`.
- Preserve per-model failure isolation so one provider cannot fail the whole comparison.
- Add new settings to `Settings` and document them in `.env.example` and `README.md`.
- Do not log prompts, API keys, or full provider responses at info level.
