"""LangChain tool-calling agent backed by an OpenAI-compatible API."""

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
    """Create and invoke the configured model agent."""

    def __init__(
        self,
        settings: Settings,
        gene_service: GeneExpressionService,
    ) -> None:
        self._settings = settings
        self._gene_service = gene_service
        self._agent = self._build_agent()
        logger.info("Initialized agent with model %s", self._settings.llm_model)

    def _build_agent(self) -> Any | None:
        """Build the agent without making a network request."""

        model = ChatOpenAI(
            api_key=self._settings.llm_api_key,
            base_url=self._settings.llm_base_url,
            model=self._settings.llm_model,
            temperature=0,
            max_retries=3,
            timeout=120,
        )

        @tool
        def get_cancer_types() -> list[str]:
            """List the cancer indications covered by the dataset."""

            return self._gene_service.get_cancer_types()

        @tool
        def get_genes() -> list[str]:
            """List all canonical genes with expression data in the dataset."""

            return self._gene_service.get_genes()

        @tool
        def get_canonical_symbol(gene_symbol: str) -> str | None:
            """Get the canonical symbol for a gene in the dataset."""

            return self._gene_service.get_canonical_symbol(gene_symbol)

        @tool
        def get_expressions_for_cancer(cancer_name: str) -> dict[str, float]:
            """Get each gene's median expression value for a cancer indication."""

            return self._gene_service.get_expressions_for_cancer(cancer_name)

        @tool
        def get_expressions_for_gene(gene_symbol: str) -> dict[str, float]:
            """Get a gene's median expression values by cancer; aliases are accepted."""

            return self._gene_service.get_expressions_for_gene(gene_symbol)

        return create_agent(
            model=model,
            tools=[
                get_cancer_types,
                get_genes,
                get_canonical_symbol,
                get_expressions_for_cancer,
                get_expressions_for_gene,
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
                self._settings.llm_model,
                type(exc).__name__,
            )
            raise
        logger.debug("Agent invocation completed")
        return result
