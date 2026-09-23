"""Chat orchestration independent of the model provider."""

from langchain_core.messages import convert_to_openai_messages

from src.agent.schemas import AgentInput, AgentOutput
from src.agent.service import AgentService
from src.chat.schemas import ChatConversation


class ChatService:
    """Convert chat conversations to and from agent messages."""

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    async def chat(self, conversation: ChatConversation) -> ChatConversation:
        """Run one stateless chat turn and return the conversation messages."""

        payload: AgentInput = {
            "messages": [
                {"role": message.role, "content": message.content}
                for message in conversation.messages
            ]
        }
        result: AgentOutput = await self._agent_service.invoke(payload)
        return ChatConversation.model_validate(
            {"messages": convert_to_openai_messages(result["messages"])}
        )
