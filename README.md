# Génie

A small proof of concept for natural language gene expression lookups over the
provided CSV. The app runs locally and calls a hosted OpenAI-compatible model
API, configured with `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`. The example
configuration uses TensorX. Other compatible APIs can be configured there.

## Run with Docker

Install Docker Engine or Docker Desktop. From the repository root, create the
environment file `.env` as shown in `.env.example` and set your API key, then
build and run:

```bash
docker build -t marw/genie .
docker run --rm --name genie -p 8000:80 --env-file .env marw/genie
```

Open <http://127.0.0.1:8000/> for Chat and Evaluate, or
<http://127.0.0.1:8000/docs> for the API docs. Stop the container with Ctrl+C.
The API key is passed in when the container starts and is excluded from the
image build context.

## Run with Podman

Install Podman. From the repository root, create the environment file `.env` as
shown in `.env.example` and set your API key, then build and run:

```bash
podman build -t marw/genie .
podman run --rm --name genie -p 8000:80 --env-file .env marw/genie
```

Open <http://127.0.0.1:8000/> for Chat and Evaluate, or
<http://127.0.0.1:8000/docs> for the API docs. Stop the container with Ctrl+C.
The API key is passed in when the container starts and is excluded from the
image build context.

## Scope

The application now provides a simple AI chat interface that will answer questions about the specific gene expressions, and very basic evaluation functionality.
When answering questions, the agent is instructed to watch for alias issues with HGNC gene names.

## Architecture decisions

### Webserver

FastAPI (https://fastapi.tiangolo.com/) was used because it's a modern and easy-to-start-with framework that even generates docs for you automatically.
Also has lots of documentation.
AGENTS.md was taken from https://github.com/zhanymkanov/fastapi-best-practices/blob/master/AGENTS.md to make coding agents adhere to common code base structure.

### Frontend

To keep things simple, the frontend is plain HTML/CSS/JS built with daisyUI (https://daisyui.com/) and AlpineJS (https://alpinejs.dev/).
NPM / React / Vite and such were deliberately skipped to reduce complexity to a minimum.

### Agents / Inference

The project uses LangChain Agents (https://docs.langchain.com/oss/python/langchain/agents) as they are very easy to set-up and can integrate nicely into tools such as LangFuse if need be.
These Agents also provide very straightforward tool usage using simple Python annotations.
Inference uses the configured OpenAI-compatible API. The example settings use
TensorX (https://tensorx.ai/) with GLM 5.3 Flash. Other compatible APIs can be
used by setting the `LLM_*` values in `.env`.
Hosted inference reduced local hardware needs and drastically simplifies this applications' setup and dependencies.
An approach including Ollama here with some small local model such as the Qwen Instruct family turned out to be much more complicated than simply choosing a hosted AI Api.

#### Tools

The original gene expression file and data access functions were deliberately extended to support more general questions about the data:
What do expressions look like in cancer? What cancers does a gene have expression data for?

Also, gene aliases are handled to reduce ambiguity with gene symbols.
The data contained one gene symbol that is only listed as an alias in the official HGNC set.
To account for this, HGNC symbols were downloaded from [here](https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt) and the original table was enriched with canonical symbols. 

### Persistence

A persistence layer was deliberately omitted to reduce complexity.
As a tradeoff, no chats are saved and the entire chat history is re-sent on every chat turn.
The application trusts assistant messages and tool result messages supplied by the client.
A production implementation must then validate integrity server-side. 
As an upside, this makes the application and API stateless.

## Limitations

The current prototype has many limitations. Some of these are:
- No local-only inference mode. The application requires an OpenAI-compatible API.
- No tracing / metrics are collected. Perspectively, LangFuse could be used here.
- No specific security screening so the application is unsafe. For example, the entire internal LangChain data structures are sent back and forth to the client. This would be trusting client-side agent and tool messages.
- No in-depth evaluation: Only very basic tests with specific output formats. No tool call chains were inspected, and no LLM-as-a-Verifier solution was implemented.
- No authentication / authorization is in place
- No persistence, so all chat interactions are lost

## AI usage

For this project Open AI Codex was used, mostly with GPT 6 Luna (max), GPT 6 Sol (high).
The evaluation functionality was mostly done by GPT 6 Astra with some manual modifications.
Luna was used for end-to-end-testing with Playwright MCP.

### Opinion about AI usage in this project

AI usage was immensely helpful here.
However, it seemed a little surprising that coding agents would often ignore project structure instructions in AGENTS.md, despite having access to it.
Sol to some degree and especially Luna had a tendency to create a lot of bloat that had to be manually refined.
End-to-end testing by Luna was very convenient and worked very well, even taking some screenshots to document its test runs.
