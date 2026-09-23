"""Request and response models for chat endpoints."""

from typing import Literal

from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """A user or assistant turn in a chat conversation."""

    role: Literal["user", "assistant", "tool"]
    content: str


class ChatConversation(BaseModel):
    """A list of user or assistant turns in a chat conversation"""

    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="Earlier turns, since no server-side persistence is configured yet.",
    )