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
  -d '{"messages":[{"type":"human","data":{"content":"What are the lung cancer targets?"}}]}'
```

There is no database or checkpointer yet. The API is therefore stateless: send earlier turns in the `messages` field when a conversation needs context.

## Evaluations

Open **Evaluate** and click **Run evaluations**. It runs eight cases three times
with fresh history, using the configured chat agent, tools, and temperature (0).
This makes paid model API calls;
no additional evaluation server, account, or dependency is needed. Results live
only in the browser until reload.

Cases and fixed expected answers are in `src/evaluations/data/cases.json`.
The suite includes the four requested questions: help, lung targets, breast
expressions, and unsupported esophageal cancer. Each gets a JSON formatting
instruction. The help case uses a simple keyword check ("gene" and "expression");
the esophageal case expects `{"covered": false, "expressions": {}}`.
Scoring compares the final JSON answer with the expected value, ignoring array
order. The canonical alias accepts either a JSON string or a one-field object
with a `canonical_symbol` key. Invalid JSON and request errors fail; there is no LLM judge. The lung
expression case follows the service's last-row-wins semantics for repeated genes
(KRAS = 0.241), rather than assuming cancer-specific expression values.
The breast case has the same caveat: BRCA2 = 0.112, not its breast-row value 0.032.

For each case, with n=3 attempts and c successes, the report estimates:

- pass@k = `1 - C(n-c, k) / C(n, k)` (at least one success).
- pass^k = `C(c, k) / C(n, k)` (all succeed).

Scores are averaged across cases for k=1,2,3.
These follow [HumanEval](https://github.com/openai/human-eval/blob/master/human_eval/evaluation.py)
and [τ-bench](https://arxiv.org/abs/2406.12045). Three attempts are a small POC
sample; with temperature 0 they may give identical answers. The runner limits
itself to three concurrent attempts per case and 120 seconds per attempt.
