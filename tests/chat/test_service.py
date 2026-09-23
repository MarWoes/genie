from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agent.service import AgentService
from src.chat.schemas import ChatConversation, ChatMessage
from src.chat.service import ChatService


@pytest.mark.asyncio
async def test_chat_passes_conversation_to_agent_and_returns_messages() -> None:
    agent_service = AsyncMock(spec=AgentService)
    agent_service.invoke.return_value = {
        "messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
    }
    chat_service = ChatService(agent_service)
    conversation = ChatConversation(
        messages=[ChatMessage(role="user", content="Hello")]
    )

    result = await chat_service.chat(conversation)

    agent_service.invoke.assert_awaited_once_with(
        {"messages": [{"role": "user", "content": "Hello"}]}
    )
    assert result == ChatConversation(
        messages=[
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there!"),
        ]
    )
