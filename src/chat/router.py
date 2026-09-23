"""HTTP routes for chat."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from src.agent.service import AgentService
from src.chat.schemas import ChatConversation
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
    response_model=ChatConversation,
    status_code=status.HTTP_200_OK,
    summary="Chat with Genie",
    description="Run one chat turn through the TensorX-powered Deep Agent.",
)
async def chat(
        payload: ChatConversation,
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatConversation:
    """Answer a chat message using client-provided history."""

    return await chat_service.chat(
        conversation=payload,
    )
