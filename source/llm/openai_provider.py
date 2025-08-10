"""
OpenAI chat provider for streaming chat completions.
Also compatible with Groq, Anthropic, and other OpenAI-compatible APIs.
"""

import asyncio
from typing import Any, AsyncGenerator, List

from llm.base import ChatMessage, ChatProvider

try:
    from openai import AsyncOpenAI
    from openai._streaming import AsyncStream
except ImportError:
    AsyncOpenAI = None  # para test sin dependencia


class OpenAIProvider(ChatProvider):
    """
    OpenAI chat provider for streaming chat completions.
    Also compatible with Groq, Anthropic, and other OpenAI-compatible APIs.
    """

    def __init__(self, api_key: str | None, model: str, base_url: str = ""):
        if AsyncOpenAI is None:
            raise RuntimeError(
                "openai package is not installed. Please install it to use OpenAIProvider."
            )
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def stream_chat(
        self, messages: List[ChatMessage], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Streams chat messages from the OpenAI API.
        """
        resp = await self.client.chat.completions.create(
            model=self.model, messages=messages, stream=True, **kwargs
        )

        if not isinstance(resp, AsyncStream):
            raise TypeError("The response is not an AsyncStream.")

        async for event in resp:
            try:
                delta = event.choices[0].delta.content or ""
            except Exception:
                delta = ""
            if delta:
                yield delta
            await asyncio.sleep(0)
