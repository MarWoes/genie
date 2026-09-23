"""Routes for the static chat frontend."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles


frontend_dir = Path(__file__).resolve().parent
static_files = StaticFiles(directory=frontend_dir / "static")
router = APIRouter(include_in_schema=False)


@router.get("/")
async def index() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


@router.get("/static/{path:path}")
async def static(path: str, request: Request) -> Response:
    return await static_files.get_response(path, request.scope)
