"""FastAPI entrypoint for the LiteLLM Model Comparator."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from model_comparator.config import Settings, get_settings
from model_comparator.service import ComparisonService
from model_comparator.use_cases import USE_CASES

ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(ROOT / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Store settings and the service once for the lifetime of the app."""
    settings = get_settings()
    app.state.settings = settings
    app.state.comparison_service = ComparisonService(settings)
    yield


app = FastAPI(title="LiteLLM Model Comparator", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the playground page."""
    settings: Settings = request.app.state.settings
    return templates.TemplateResponse(
        request,
        "index.html",
        {"models": settings.models, "use_cases": USE_CASES},
    )


@app.get("/health")
async def health() -> JSONResponse:
    """Report that the web process is ready; providers are checked per request."""
    return JSONResponse({"status": "ok"})


@app.get("/use-cases")
async def use_cases() -> JSONResponse:
    """Return the catalogue of pre-built use-case prompts as JSON."""
    return JSONResponse(
        [
            {
                "id": uc.id,
                "category": uc.category,
                "title": uc.title,
                "prompt": uc.prompt,
            }
            for uc in USE_CASES
        ]
    )


@app.post("/compare", response_class=HTMLResponse)
async def compare(request: Request, prompt: str = Form(min_length=1)) -> HTMLResponse:
    """Run configured models for a prompt and render a result fragment."""
    settings: Settings = request.app.state.settings
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        return templates.TemplateResponse(
            request,
            "results.html",
            {"comparison": None, "error": "Enter a prompt."},
            status_code=422,
        )
    if len(cleaned_prompt) > settings.max_prompt_characters:
        message = f"Prompt must be at most {settings.max_prompt_characters:,} characters."
        return templates.TemplateResponse(
            request, "results.html", {"comparison": None, "error": message}, status_code=422
        )

    service: ComparisonService = request.app.state.comparison_service
    comparison = await service.compare(cleaned_prompt)
    return templates.TemplateResponse(
        request, "results.html", {"comparison": comparison, "error": None}
    )
