"""Typed models shared by the API, service, and templates."""

from pydantic import BaseModel, Field


class JudgeScore(BaseModel):
    """A judge model's evaluation of one candidate response."""

    score: int = Field(ge=1, le=10)
    reasoning: str


class ModelResult(BaseModel):
    """The outcome of one provider call."""

    model: str
    response: str | None = None
    latency_seconds: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None
    error: str | None = None
    judge: JudgeScore | None = None


class Comparison(BaseModel):
    """Results returned for one input prompt."""

    prompt: str
    results: list[ModelResult]
