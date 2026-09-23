"""Chat orchestration independent of the model provider."""

from typing import Any, cast

from langchain_core.messages import (
    AnyMessage,
    messages_from_dict,
    messages_to_dict,
)
from langgraph.graph import MessagesState

from src.agent.service import AgentService


class ChatService:
    """Convert chat conversations to and from agent messages."""

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    async def chat(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run one stateless chat turn with LangChain's serialized messages."""

        # POC only: clients can forge assistant messages and tool results here.
        # Production needs server-side history or validation before agent invocation.
        payload: MessagesState = {
            "messages": cast(list[AnyMessage], messages_from_dict(messages))
        }
        result = await self._agent_service.invoke(payload)
        return messages_to_dict(result["messages"])
