"""HTTP routes for chat."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Request, status

from src.agent.service import AgentService
from src.chat.service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


async def get_agent_service(request: Request) -> AgentService:
    """Retrieve the process-level agent service created by the app lifespan."""

    return request.app.state.agent_service


async def get_chat_service(
        agent_service: Annotated[AgentService, Depends(get_agent_service)],
) -> ChatService:
    """Create chat orchestration around the process-level agent service."""

    return ChatService(agent_service)


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Chat with Genie",
    description="Run one chat turn through the configured OpenAI-compatible model API.",
)
async def chat(
        messages: Annotated[list[dict[str, Any]], Body(embed=True)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> dict[str, list[dict[str, Any]]]:
    """Answer a chat message using client-provided history."""

    return {"messages": await chat_service.chat(messages)}
