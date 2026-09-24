# Génie

A small proof of concept for natural language gene expression lookups over the
provided CSV. It runs locally with a hosted, OpenAI-compatible TensorX
model; it does not need a GPU or a separate tracing/evaluation server.

## Run with Docker

Install Docker Engine or Docker Desktop. From the repository root, create the
environment file `.env` and set your TensorX API key, then build and run:

```bash
docker build -t genie .
docker run --rm --name genie -p 8000:80 --env-file .env genie
```

Open <http://127.0.0.1:8000/> for Chat and Evaluate, or
<http://127.0.0.1:8000/docs> for the API docs. Stop the container with Ctrl+C.
The API key is passed in when the container starts and is excluded from the
image build context.

## Run with Podman

Install Podman. From the repository root, create the
environment file `.env` and set your TensorX API key, then build and run:

```bash
podman build -t genie .
podman run --rm --name genie -p 8000:80 --env-file .env genie
```

Open <http://127.0.0.1:8000/> for Chat and Evaluate, or
<http://127.0.0.1:8000/docs> for the API docs. Stop the container with Ctrl+C.
The API key is passed in when the container starts and is excluded from the
image build context.

## Architecture and behavior

The browser sends LangChain's serialized message history to FastAPI. `ChatService`
converts it to LangChain messages and calls `AgentService`, which uses
`langchain.agents.create_agent` with the configured `ChatOpenAI` adapter. The
agent can call five local tools backed by `GeneExpressionService`; that service
loads the bundled CSV once. The same agent powers the
evaluation page. Evaluation cases and expected answers live in
`src/evaluations/data/cases.json`.

The app is stateless: conversation history stays in the browser and is sent on
each request. This keeps the POC small and needs no database, but the server
currently trusts client-provided history. Do not expose this setup as a
production service without validating or storing conversation history safely.

The gene service maps aliases to canonical symbols. Its tools list covered
cancers and genes, look up aliases, return all gene expressions for one cancer,
or return one gene's expressions across cancers. For example, HER2 resolves to
ERBB2, with 0.42 in breast and 0.67 in gastric cancer. KRAS is 0.359 in lung
and 0.241 in pancreatic cancer. Keeping cancer in each result avoids the
provided gene-only example's “last matching row” ambiguity. Unknown cancers
or genes return no values. Cross-cancer differences are descriptive only:
the CSV does not specify units or normalization for biological comparisons.

The eight evaluation cases use fixed expected JSON values; help is checked for
the words “gene” and “expression”. Lists ignore order. There is no LLM judge or
tool-call trace validation, so this is a small smoke check rather than a full
measure of conversational quality. Each run makes 24 agent requests (eight
cases × three attempts), plus any tool-follow-up requests, and results are not
saved. It calculates pass@k (at least one of k attempts succeeds) and pass^k
(all k attempts succeed), averaged across cases. With temperature 0, the three
attempts may return identical answers.

The manual demo questions are: “How can you help me?”, “What are the main genes
involved in lung cancer?”, “What is the median value expression of genes
involved in breast cancer?”, and “What is the median value expression of genes
involved in esophageal cancer?”, and “What are the expression values for KRAS
across cancers?” The esophageal question should be answered as “not covered by
this dataset”; it does not mean that esophageal cancer has no relevant genes.

## AI-assisted coding: trade-offs

AI assistance sped up scaffolding, repetitive wiring, and the first evaluation
UI. It also made confident assumptions about tool message formats and gene
aliases that needed checking against the installed library behavior and CSV.
Generated code can add unnecessary dependencies or tests that pass its own
assumptions without checking the task's real semantics. I kept the tools and
evaluation local, reviewed the lookups against the CSV, and made the limitations
visible rather than treating model-generated answers as ground truth.
