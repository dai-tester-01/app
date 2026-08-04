import asyncio
import json

import pytest

from model_comparator.config import Settings
from model_comparator.service import ComparisonService


def completion(content: str, *, cost: float = 0.002) -> dict[str, object]:
    return {
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        "_hidden_params": {"response_cost": cost},
    }


@pytest.mark.asyncio
async def test_compare_runs_models_concurrently_and_keeps_individual_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active = 0
    max_active = 0

    async def fake_completion(**kwargs: object) -> dict[str, object]:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        if kwargs["model"] == "bad-model":
            raise RuntimeError("invalid credentials")
        return completion(f"response from {kwargs['model']}")

    monkeypatch.setattr("model_comparator.service.acompletion", fake_completion)
    service = ComparisonService(Settings(models=["good-model", "bad-model"]))

    comparison = await service.compare("Hello")

    assert max_active == 2
    good, bad = comparison.results
    assert good.response == "response from good-model"
    assert good.total_tokens == 30
    assert good.cost_usd == 0.002
    assert bad.error == "invalid credentials"


@pytest.mark.asyncio
async def test_compare_attaches_optional_judge_scores(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_completion(**kwargs: object) -> dict[str, object]:
        if kwargs["model"] == "judge-model":
            return completion(
                json.dumps(
                    {
                        "scores": {
                            "model-a": {"score": 9, "reasoning": "Clear and accurate."},
                            "model-b": {"score": 6, "reasoning": "Too brief."},
                        }
                    }
                )
            )
        return completion(f"response from {kwargs['model']}")

    monkeypatch.setattr("model_comparator.service.acompletion", fake_completion)
    service = ComparisonService(Settings(models=["model-a", "model-b"], judge_model="judge-model"))

    comparison = await service.compare("Hello")

    assert comparison.results[0].judge is not None
    assert comparison.results[0].judge.score == 9
    assert comparison.results[1].judge is not None
    assert comparison.results[1].judge.reasoning == "Too brief."
