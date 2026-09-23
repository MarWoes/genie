"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.agent.service import AgentService
from src.chat.router import router as chat_router
from src.config import settings
from src.evaluations.router import router as evaluations_router
from src.evaluations.service import EvaluationService
from src.frontend.router import router as frontend_router
from src.genes.service import GeneExpressionService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create application services when the FastAPI process starts."""

    genes = GeneExpressionService()
    app.state.agent_service = AgentService(settings, genes)
    app.state.evaluation_service = EvaluationService(settings, app.state.agent_service)
    yield


app = FastAPI(
    title="Genie API",
    description="A lightweight gene information assistant.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return a simple liveness response."""

    return {"status": "ok"}


app.include_router(chat_router)
app.include_router(evaluations_router)
app.include_router(frontend_router)
