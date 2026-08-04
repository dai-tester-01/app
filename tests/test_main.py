from fastapi.testclient import TestClient

from model_comparator.config import Settings
from model_comparator.main import app
from model_comparator.models import Comparison, ModelResult


def test_home_and_health_are_available() -> None:
    with TestClient(app) as client:
        home = client.get("/")
        health = client.get("/health")

    assert home.status_code == 200
    assert "Compare models side by side" in home.text
    assert health.json() == {"status": "ok"}


def test_compare_renders_result_and_rejects_oversized_prompt() -> None:
    class FakeService:
        async def compare(self, prompt: str) -> Comparison:
            return Comparison(
                prompt=prompt,
                results=[
                    ModelResult(
                        model="test-model",
                        response="A useful answer.",
                        latency_seconds=0.5,
                        total_tokens=42,
                        cost_usd=0.001,
                    )
                ],
            )

    with TestClient(app) as client:
        app.state.settings = Settings(models=["test-model"], max_prompt_characters=5)
        app.state.comparison_service = FakeService()

        successful = client.post("/compare", data={"prompt": "hello"})
        invalid = client.post("/compare", data={"prompt": "too long"})

    assert successful.status_code == 200
    assert "A useful answer." in successful.text
    assert invalid.status_code == 422
    assert "at most 5 characters" in invalid.text
