"""Concurrent LiteLLM orchestration with isolated model failures."""

import asyncio
import json
import logging
from time import perf_counter
from typing import Any

from litellm import acompletion

from model_comparator.config import Settings
from model_comparator.models import Comparison, JudgeScore, ModelResult

logger = logging.getLogger(__name__)


def _value(source: object, name: str) -> Any:
    """Read a field from either LiteLLM's object-like or dict-like responses."""
    if isinstance(source, dict):
        return source.get(name)
    return getattr(source, name, None)


def _message_content(response: object) -> str:
    choices = _value(response, "choices") or []
    if not choices:
        raise ValueError("Provider returned no response choices")
    message = _value(choices[0], "message")
    content = _value(message, "content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Provider returned an empty response")
    return content.strip()


def _usage_fields(response: object) -> tuple[int | None, int | None, int | None]:
    usage = _value(response, "usage")
    prompt_tokens = _value(usage, "prompt_tokens")
    completion_tokens = _value(usage, "completion_tokens")
    total_tokens = _value(usage, "total_tokens")
    return (
        prompt_tokens if isinstance(prompt_tokens, int) else None,
        completion_tokens if isinstance(completion_tokens, int) else None,
        total_tokens if isinstance(total_tokens, int) else None,
    )


def _response_cost(response: object) -> float | None:
    hidden_params = _value(response, "_hidden_params") or {}
    cost = _value(hidden_params, "response_cost")
    return float(cost) if isinstance(cost, int | float) else None


class ComparisonService:
    """Compare configured models and optionally obtain a separate judge score."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def compare(self, prompt: str) -> Comparison:
        """Run all model calls concurrently, then score successful candidates."""
        results = await asyncio.gather(
            *(self._call_model(model, prompt) for model in self.settings.models)
        )
        if self.settings.judge_model:
            await self._judge_successful_results(prompt, results)
        return Comparison(prompt=prompt, results=results)

    async def _call_model(self, model: str, prompt: str) -> ModelResult:
        started = perf_counter()
        timeout = self.settings.model_timeouts.get(model, self.settings.request_timeout_seconds)
        try:
            response = await acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )
            prompt_tokens, completion_tokens, total_tokens = _usage_fields(response)
            return ModelResult(
                model=model,
                response=_message_content(response),
                latency_seconds=perf_counter() - started,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=_response_cost(response),
            )
        except Exception as exc:  # Provider SDK errors must not stop peer requests.
            logger.warning("Model comparison failed", extra={"model": model, "error": str(exc)})
            return ModelResult(
                model=model,
                latency_seconds=perf_counter() - started,
                error=str(exc),
            )

    async def _judge_successful_results(self, prompt: str, results: list[ModelResult]) -> None:
        candidates = [result for result in results if result.response]
        if not candidates or self.settings.judge_model is None:
            return

        payload = {
            "prompt": prompt,
            "responses": [{"model": item.model, "response": item.response} for item in candidates],
        }
        instruction = (
            "Evaluate each candidate response for the user's prompt. Return JSON only: "
            '{"scores": {"model name": {"score": 1-10, "reasoning": "brief reason"}}}. '
            f"Input: {json.dumps(payload)}"
        )
        try:
            response = await acompletion(
                model=self.settings.judge_model,
                messages=[{"role": "user", "content": instruction}],
                response_format={"type": "json_object"},
                timeout=self.settings.request_timeout_seconds,
            )
            scores = json.loads(_message_content(response)).get("scores", {})
            for result in candidates:
                raw_score = scores.get(result.model)
                if isinstance(raw_score, dict):
                    result.judge = JudgeScore.model_validate(raw_score)
        except Exception as exc:  # Scoring is additive; comparison remains useful without it.
            logger.warning(
                "Judge evaluation failed",
                extra={"model": self.settings.judge_model, "error": str(exc)},
            )
