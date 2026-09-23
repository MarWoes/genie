"""TensorX-backed agent integration."""

from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.agent.schemas import AgentInput, AgentOutput
from src.config import Settings

SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent / "data" / "system_prompt.txt"


class AgentService:
    """Create and invoke the TensorX-powered Deep Agent."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._agent = self._build_agent()

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

        return create_agent(
            model=model,
            tools=[],
            system_prompt=SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"),
        )

    async def invoke(self, payload: AgentInput) -> AgentOutput:
        """Invoke the configured agent and return its message state."""
        return await self._agent.ainvoke(payload)
