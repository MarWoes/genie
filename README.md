# Génie - Your friendly gene agent

## What is this?


The goal is to create a small project for an AI agent that will assist users when searching for gene information.

## Run locally

Create and activate the project virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your TensorX API key. TensorX exposes an OpenAI-compatible API, so the app uses LangChain's `ChatOpenAI` adapter with TensorX's base URL.

Start the API from the project root:

```bash
uvicorn main:app --reload
```

You can also run `main.py` directly from PyCharm after selecting the project `.venv` interpreter.

The chat page is available at `http://127.0.0.1:8000/`. Open `http://127.0.0.1:8000/docs` for the interactive API documentation. The page is served directly from `src/frontend`, with no frontend build step.

## Chat endpoint

`POST /chat` accepts a client-managed conversation and returns its updated messages:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"What does BRCA1 do?"}]}'
```

There is no database or checkpointer yet. The API is therefore stateless: send earlier turns in the `messages` field when a conversation needs context.
