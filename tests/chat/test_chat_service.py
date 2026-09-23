from unittest.mock import AsyncMock

import pytest
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    message_to_dict,
    messages_to_dict,
)

from src.agent.service import AgentService
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
    result = await chat_service.chat([message_to_dict(HumanMessage(content="Hello"))])

    agent_service.invoke.assert_awaited_once_with(
        {"messages": [HumanMessage(content="Hello")]}
    )
    assert result == messages_to_dict(
        [HumanMessage(content="Hello"), AIMessage(content="Hi there!")]
    )


@pytest.mark.asyncio
async def test_chat_preserves_tool_calls_across_requests() -> None:
    tool_call = {
        "name": "get_expressions_for_cancer",
        "args": {"cancer_name": "lung"},
        "id": "call_1",
        "type": "tool_call",
    }
    agent_service = AsyncMock(spec=AgentService)
    agent_service.invoke.return_value = {
        "messages": [
            HumanMessage(content="Find targets"),
            AIMessage(content="", tool_calls=[tool_call]),
            ToolMessage(
                content="{'EGFR': 0.1}",
                tool_call_id="call_1",
                name="get_expressions_for_cancer",
            ),
            AIMessage(content="EGFR is a target."),
        ]
    }
    chat_service = ChatService(agent_service)

    first = await chat_service.chat(
        [message_to_dict(HumanMessage(content="Find targets"))]
    )
    assert first[1]["data"]["tool_calls"][0]["id"] == "call_1"
    assert first[2]["data"]["tool_call_id"] == "call_1"

    await chat_service.chat(
        [*first, message_to_dict(HumanMessage(content="And more?"))]
    )
    replayed = agent_service.invoke.call_args.args[0]["messages"]
    assert isinstance(replayed[1], AIMessage)
    assert replayed[1].tool_calls == [tool_call]
    assert isinstance(replayed[2], ToolMessage)
    assert replayed[2].tool_call_id == "call_1"
    assert isinstance(replayed[-1], HumanMessage)
