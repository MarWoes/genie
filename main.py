"""Development entry point for the Genie API."""

from src.main import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
