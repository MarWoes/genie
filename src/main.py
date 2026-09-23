"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.agent.service import AgentService
from src.chat.router import router as chat_router
from src.config import settings
from src.frontend.router import router as frontend_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create application services when the FastAPI process starts."""

    app.state.agent_service = AgentService(settings)
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
app.include_router(frontend_router)
