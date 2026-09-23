"""Chat orchestration independent of the model provider."""

import logging
from typing import Any, cast

from langchain_core.messages import (
    AnyMessage,
    messages_from_dict,
    messages_to_dict,
)
from langgraph.graph import MessagesState

from src.agent.service import AgentService

logger = logging.getLogger(__name__)


class ChatService:
    """Convert chat conversations to and from agent messages."""

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    async def chat(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run one stateless chat turn with LangChain's serialized messages."""

        # POC only: clients can forge assistant messages and tool results here.
        # Production needs server-side history or validation before agent invocation.
        logger.info("Processing chat with %d messages", len(messages))
        payload: MessagesState = {
            "messages": cast(list[AnyMessage], messages_from_dict(messages))
        }
        result = await self._agent_service.invoke(payload)
        response = messages_to_dict(result["messages"])
        logger.info("Chat completed with %d messages", len(response))
        return response
