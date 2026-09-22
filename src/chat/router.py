"""HTTP routes for chat."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from openai import OpenAIError

from src.chat.schemas import ChatConversation
from src.chat.service import AgentConfigurationError, AgentService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


async def get_agent_service(request: Request) -> AgentService:
    """Retrieve the process-level agent service created by the app lifespan."""

    return request.app.state.agent_service


@router.post(
    "",
    response_model=ChatConversation,
    status_code=status.HTTP_200_OK,
    summary="Chat with Genie",
    description="Run one chat turn through the TensorX-powered Deep Agent."
)
async def chat(
    payload: ChatConversation,
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
) -> ChatConversation:
    """Answer a chat message using client-provided history."""

    try:
        return await agent_service.chat(
            conversation=payload,
        )
    except AgentConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except OpenAIError as exc:
        logger.exception("TensorX request failed with %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="TensorX did not return a successful model response.",
        ) from exc
