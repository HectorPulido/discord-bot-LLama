"""
This module provides a MessageHandler class for processing Discord messages.
It handles incoming messages, checks if a response is needed, builds a chat context,
and streams a response using a chat provider.
"""

import re
import asyncio
from typing import List, Dict

import discord

from core.config import Settings

from core.stream import StreamEditor
from llm.openai_provider import OpenAIProvider
from addons.emoji_only_channel import manage_emojis_channel
from addons.commands import (
    change_status,
    generate_image,
    ping,
)
from addons.stable_diffusion_conection import SDClient


class MessageHandler:
    """
    Class to handle incoming Discord messages and respond using a chat provider.
    It checks if the message should be responded to, builds the chat context,
    and streams the response back to the channel.
    """

    def __init__(
        self,
        settings: Settings,
        provider: OpenAIProvider,
        bot_user: discord.ClientUser | None,
    ):
        self.provider = provider
        self.bot_user = bot_user
        self.settings = settings
        self.prompt = self.settings.base_prompt
        self.discord_commands = self._initialize_commands()
        self.stable_diffusion_connection = self._initialize_stable_diffusion()

    def _initialize_stable_diffusion(self):
        if not self.settings.use_stable_diffusion:
            return None
        if not self.settings.sd_url or not self.settings.sd_checkpoint:
            raise ValueError(
                "Stable Diffusion is enabled but SD_URL or SD_CHECKPOINT is not set."
            )
        return SDClient(
            url=self.settings.sd_url,
            sd_checkpoint=self.settings.sd_checkpoint,
            steps=15,
        )

    def _initialize_commands(self):
        """
        Initialize the commands that the bot can respond to.
        This method should be called after the bot is ready.
        """
        return {
            "!change_status": change_status,
            "!generate-image": generate_image,
            "!ping": ping,
        }

    def _manage_commands(self, message):
        """
        Check if the message starts with a command and handle it accordingly.
        """
        for command, handler in self.discord_commands.items():
            if message.content.startswith(command):
                asyncio.create_task(
                    handler(
                        self,
                        message,
                    )
                )
                return True
        return False

    def _is_valid_channel(self, message, channels) -> bool:
        """
        Check if a message is in a valid channel.
        """
        if message.guild is None or message.channel is None:
            return False

        final_id = f"{message.guild.id}:{message.channel.id}"
        for channel in channels:
            if re.search(channel, final_id):
                return True

        return False

    def _should_respond(self, message: discord.Message) -> bool:
        if not self.bot_user:
            return False
        if message.author.bot:
            return False
        if self.settings.mention_required:
            return any(u.id == self.bot_user.id for u in message.mentions)
        return True

    async def build_context_from_channel(self, channel):
        """
        Build the chat context from the channel's message history.
        """

        msgs: List[discord.Message] = []
        async for m in channel.history(
            limit=self.settings.max_context_messages, oldest_first=False
        ):
            if m.content is None:
                continue
            msgs.append(m)
        msgs = list(reversed(msgs))

        chat: List[Dict[str, str]] = []
        if self.prompt:
            chat.append({"role": "system", "content": self.prompt})

        for m in msgs:
            role = (
                "assistant"
                if (self.bot_user and m.author.id == self.bot_user.id)
                else "user"
            )
            content = m.content
            author = m.author.display_name
            if not content:
                continue
            chat.append({"role": role, "content": f"{author} said: {content}"})
        return chat

    async def handle_message(self, message: discord.Message):
        """
        Handle an incoming message by checking if a response is needed,
        building the chat context, and streaming the response.
        """

        # Manage emoji-only channels
        if self._is_valid_channel(message, self.settings.emoji_only_channels_data):
            await manage_emojis_channel(message)
            return

        if not self._is_valid_channel(message, self.settings.chat_channels_data):
            return

        if self._manage_commands(message):
            return

        if not self._should_respond(message):
            return

        chat_messages = await self.build_context_from_channel(
            message.channel,
        )

        asyncio.create_task(self._run_stream(chat_messages, message))

    async def _run_stream(self, chat_messages, message: discord.Message):
        editor = StreamEditor(
            message,
            safe_edit_length=self.settings.safe_edit_length,
            edit_every_n_chunks=self.settings.edit_every_n_chunks,
            edit_min_interval_ms=self.settings.edit_min_interval_ms,
        )
        try:
            stream = self.provider.stream_chat(chat_messages, temperature=0.2)
            async for chunk in stream:
                await editor.on_stream_chunk(chunk, force=False)
            await editor.on_stream_chunk("", force=True)
        except Exception as e:
            print(f"Error processing message: {e}")
            await message.channel.send(
                "An error occurred while processing your message, please contact support."
            )
