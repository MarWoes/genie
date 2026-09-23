from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import AIMessage, HumanMessage

from src.agent.service import AgentService
from src.chat.router import get_agent_service, router


@pytest.mark.asyncio
async def test_chat_endpoint_uses_injected_agent_service() -> None:
    app = FastAPI()
    app.include_router(router)

    agent_service = AsyncMock(spec=AgentService)
    agent_service.invoke.return_value = {
        "messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
    }
    app.dependency_overrides[get_agent_service] = lambda: agent_service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )

    assert response.status_code == 200
    assert response.json() == {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
    }
    agent_service.invoke.assert_awaited_once_with(
        {"messages": [{"role": "user", "content": "Hello"}]}
    )
