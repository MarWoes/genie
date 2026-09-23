"""Deep Agent orchestration for the chat domain."""

from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import convert_to_openai_messages
from langchain_openai import ChatOpenAI

from src.chat.schemas import ChatConversation
from src.config import Settings


class AgentConfigurationError(RuntimeError):
    """Raised when the model cannot be used with the current configuration."""


class AgentService:
    """Create and invoke the TensorX-powered Deep Agent."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._agent = self._build_agent()

    def _build_agent(self) -> Any | None:
        """Build the agent without making a network request."""

        if not self._settings.tensorx_api_key:
            return None

        # Disable all default tools just in case something bad could happen
        # See https://docs.langchain.com/oss/python/deepagents/overview#running-without-the-default-filesystem-tools
        tensorx_model = self._settings.tensorx_model

        model = ChatOpenAI(
            api_key=self._settings.tensorx_api_key,
            base_url=self._settings.tensorx_base_url,
            model=tensorx_model,
            temperature=0,
            max_retries=2,
            timeout=120,
        )

        return create_agent(
            model=model,
            tools=[],
            system_prompt=(
                """
                You are Génie. An AI assistant whose sole purpose is to assist with simple gene expression lookups.
                You MUST ONLY answer questions similar to the following:
                - How can you help me?
                - What are the main genes involved in lung cancer?
                - What is the median value expression of genes involved in breast cancer?
                Your answer MUST be based ONLY on tool call information.
                NEVER provide gene information solely from memory or speculate about function.
                ONLY exactly answer those questions simple and brief, but polite.
                If you do not receive information from a tool call for whatever reason, only tell the user you have no reliable information.                  
                """
            ),
        )

    async def chat(
            self,
            conversation: ChatConversation,
    ) -> ChatConversation:
        """Run one stateless chat turn and return the final assistant text."""

        if self._agent is None:
            raise AgentConfigurationError(
                "TENSORX_API_KEY is not configured. Copy .env.example to .env "
                "and add your TensorX API key."
            )

        result = await self._agent.ainvoke(
            conversation.model_dump()
        )

        return ChatConversation.model_validate(
            {
                "messages": convert_to_openai_messages(
                    result["messages"]
                )
            }
        )
