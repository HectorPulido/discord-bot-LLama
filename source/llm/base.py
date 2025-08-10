from typing import AsyncGenerator, Protocol, List, Dict, Any

# {"role": "system|user|assistant", "content": "..."}
ChatMessage = Dict[str, str]


class ChatProvider(Protocol):
    """
    Protocol for chat providers that can handle streaming chat messages.
    """

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Streams chat messages from the provider.
        """
        raise NotImplementedError("stream_chat must be implemented by the provider.")
