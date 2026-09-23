"""Types for the agent's input and output state."""

from typing import Literal, TypedDict

from langchain_core.messages import BaseMessage


class AgentInputMessage(TypedDict):
    role: Literal["user", "assistant", "tool"]
    content: str


class AgentInput(TypedDict):
    messages: list[AgentInputMessage]


class AgentOutput(TypedDict):
    messages: list[BaseMessage]
