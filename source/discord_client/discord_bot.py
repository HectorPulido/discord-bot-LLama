"""
Discord client class.
"""

import re
import logging
import asyncio
import discord
from discord.ext.commands import Bot

from memory_models import MultiChannelMemory
from translator import Translator
from llms_models import GeneralLLMModel
from extra import clear_memory, change_status, manage_emojis_channel
from utils import is_valid_channel


class DiscordLLMBot(Bot):
    """
    This class represents a Discord bot that uses a GPT-3 model to respond to messages.
    """

    def __init__(
        self,
        model_name: str,
        channel_data: str,
        ollama_url: str,
        memory_size: int = 5,
        use_translator: bool = False,
    ):
        translator = None
        if use_translator:
            logging.info("Using translator...")
            translator = Translator()

        self.model = GeneralLLMModel(
            model_name,
            translator,
            prompt_path="prompts/base_prompt.txt",
            temp=0.9,
            ollama_url=ollama_url,
        )
        self.memories = MultiChannelMemory(
            memory_size=memory_size, load_path="memory.mem"
        )
        self.model_lock = False
        self.discord_commands = {
            "!change_status": change_status,
            "!clear": clear_memory,
        }
        self.channel_data = channel_data

        self.memory_size = memory_size

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def _check_commands(self, message):
        for command, func in self.discord_commands.items():
            if command in message.content:
                await func(self, message)
                return True
        return False

    async def _llm_response(self, message):
        if not is_valid_channel(message, self.channel_data["CHAT_CHANNELS"]):
            await message.reply("Sorry, I can't talk here.", mention_author=True)
            return

        while self.model_lock:
            logging.info("Waiting for model to unlock...")
            await asyncio.sleep(10)

        message_text = str(message.content)
        message_text = re.sub(r"<@\d+>", "", message_text).strip()[-100:]
        message_text = f"{message.author.display_name}: {message_text}"

        logging.info("Message received in %s: %s", message.channel.id, message_text)

        async with message.channel.typing():
            self.model_lock = True
            memory = self.memories.get_memory(message.channel.id)
            response = await self.model.evaluate(message_text, memory=memory)
            logging.info("Response: %s", response)
            await message.reply(response, mention_author=True)
            self.memories.persist_memory()

        await asyncio.sleep(1)
        self.model_lock = False

    async def on_ready(self):
        """Called when the bot is ready."""
        logging.info("Bot %s is connected to server.", self.user.display_name)

    async def on_message(self, message):
        """Called when a message is sent in a channel the bot is in."""
        if message.author == self.user:
            return

        await self._check_commands(message)

        await manage_emojis_channel(message, self.channel_data["EMOJI_ONLY_CHANNELS"])

        if not self.user.mentioned_in(message):
            return

        await self._llm_response(message)
