"""Run a fixed evaluation suite without an external evaluation server."""

import asyncio
import json
from math import comb
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.errors import GraphRecursionError
from openai import APIError

from src.agent.service import AgentService
from src.config import Settings

RUNS = 3
CASES_PATH = Path(__file__).resolve().parent / "data" / "cases.json"


def calculate_metrics(correct_counts: list[int]) -> list[dict[str, float | int]]:
    """Estimate at-least-one and all-success probabilities, averaged per case."""

    metrics = []
    for k in range(1, RUNS + 1):
        possible_groups = comb(RUNS, k)
        pass_at_k = 0.0
        pass_hat_k = 0.0

        for successes in correct_counts:
            failures = RUNS - successes
            # At least one succeeds unless every attempt in the group fails.
            pass_at_k += 1 - comb(failures, k) / possible_groups
            pass_hat_k += comb(successes, k) / possible_groups

        metrics.append({
            "k": k,
            "pass_at_k": pass_at_k / len(correct_counts),
            "pass_hat_k": pass_hat_k / len(correct_counts),
        })
    return metrics


def matches_expected(actual: Any, case: dict[str, Any]) -> bool:
    """Compare JSON answers, allowing unordered lists and the configured wrapper."""

    expected = case["expected"]
    answer_key = case.get("answer_key")
    if answer_key and isinstance(actual, dict) and list(actual) == [answer_key]:
        actual = actual[answer_key]

    if type(actual) is not type(expected):
        return False

    if isinstance(expected, list):
        if not all(isinstance(item, str) for item in actual):
            return False
        return sorted(actual) == sorted(expected)

    return actual == expected


class EvaluationService:
    def __init__(self, settings: Settings, agent: AgentService) -> None:
        self.settings = settings
        self.agent = agent
        self.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    async def run(self) -> dict[str, Any]:
        results = []
        correct_counts = []

        for case in self.cases:
            pending_attempts = [self._run_attempt(case) for _ in range(RUNS)]
            attempts = await asyncio.gather(*pending_attempts)
            results.append({**case, "attempts": attempts})
            correct_counts.append(sum(attempt["passed"] for attempt in attempts))

        return {
            "model": self.settings.tensorx_model,
            "runs": RUNS,
            "cases": results,
            "metrics": calculate_metrics(correct_counts),
        }

    async def _run_attempt(self, case: dict[str, Any]) -> dict[str, Any]:
        prompt = case["prompt"] + " Return only valid JSON, without markdown or explanation."
        try:
            # Each attempt starts with fresh history; no checkpointer is configured.
            result = await asyncio.wait_for(
                self.agent.invoke({"messages": [HumanMessage(content=prompt)]}),
                timeout=120,
            )
        except (APIError, TimeoutError, GraphRecursionError) as exc:
            # Failed requests remain failed attempts, visible in the report.
            return {"passed": False, "answer": "", "error": str(exc)[:300]}

        answer = ""
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage):
                answer = str(message.text)
                break

        try:
            actual = json.loads(answer)
        except json.JSONDecodeError:
            return {"passed": False, "answer": answer, "error": "Expected valid JSON."}

        return {
            "passed": matches_expected(actual, case),
            "answer": answer,
            "error": None,
        }
