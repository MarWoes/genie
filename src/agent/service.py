"""TensorX-backed agent integration."""

import logging
from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from src.config import Settings
from src.genes.service import GeneExpressionService

SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent / "data" / "system_prompt.txt"
logger = logging.getLogger(__name__)


class AgentService:
    """Create and invoke the TensorX-powered Deep Agent."""

    def __init__(
        self,
        settings: Settings,
        gene_service: GeneExpressionService,
    ) -> None:
        self._settings = settings
        self._gene_service = gene_service
        self._agent = self._build_agent()
        logger.info("Initialized agent with model %s", self._settings.tensorx_model)

    def _build_agent(self) -> Any | None:
        """Build the agent without making a network request."""

        model = ChatOpenAI(
            api_key=self._settings.tensorx_api_key,
            base_url=self._settings.tensorx_base_url,
            model=self._settings.tensorx_model,
            temperature=0,
            max_retries=2,
            timeout=120,
        )

        @tool
        def get_targets(cancer_name: str) -> list[str]:
            """Get canonical gene targets for a cancer indication."""

            return self._gene_service.get_targets(cancer_name)

        @tool
        def get_cancer_types() -> list[str]:
            """List the cancer indications covered by the take-home dataset."""

            return self._gene_service.get_cancer_types()

        @tool
        def get_canonical_symbol(gene_symbol: str) -> str | None:
            """Get the canonical symbol for a gene in the take-home dataset."""

            return self._gene_service.get_canonical_symbol(gene_symbol)

        @tool
        def get_expressions(genes: list[str]) -> dict[str, float]:
            """Get median expression values for gene symbols."""

            return self._gene_service.get_expressions(genes)

        return create_agent(
            model=model,
            tools=[
                get_targets,
                get_cancer_types,
                get_canonical_symbol,
                get_expressions,
            ],
            system_prompt=SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"),
        )

    async def invoke(self, payload: MessagesState) -> MessagesState:
        """Invoke the configured agent and return its message state."""
        logger.debug("Invoking agent with %d messages", len(payload["messages"]))
        try:
            result = await self._agent.ainvoke(payload)
        except Exception as exc:
            logger.error(
                "Agent invocation failed (model=%s, error_type=%s)",
                self._settings.tensorx_model,
                type(exc).__name__,
            )
            raise
        logger.debug("Agent invocation completed")
        return result
