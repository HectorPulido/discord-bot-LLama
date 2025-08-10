"""
This module initializes the Discord bot, sets up the OpenAI provider, and handles incoming messages.
It listens for messages, checks if a response is needed, builds the chat context,
and streams a response back to the channel.
"""

import discord
import asyncio
from core.config import Settings
from llm.openai_provider import OpenAIProvider
from handlers.message_handler import MessageHandler

intents = discord.Intents.default()
intents.message_content = True


async def main():
    """
    Main function to initialize the Discord bot and set up the message handler.
    It retrieves settings, initializes the Discord client, and starts listening for messages.
    """
    settings = Settings.get_settings()
    client = discord.Client(intents=intents)
    provider: OpenAIProvider | None = None
    handler: MessageHandler | None = None

    @client.event
    async def on_ready():
        if not client or not client.user:
            raise ValueError(
                "Discord client user is not set. Ensure the bot is logged in."
            )
        print(f"Logged as {client.user} (id={client.user.id})")

        nonlocal provider, handler

        provider = OpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.model,
            base_url=settings.llm_base_url,
        )
        handler = MessageHandler(settings, provider, client.user)

    @client.event
    async def on_message(message: discord.Message):
        if not handler:
            print("Handler is not initialized yet.")
            return
        await handler.handle_message(message)

    await client.start(settings.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
