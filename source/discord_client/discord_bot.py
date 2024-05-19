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
from extra import clear_memory, change_status, manage_emojis_channel, generate_image
from utils import is_valid_channel
from sd_model import SDClient


class DiscordLLMBot(Bot):
    """
    This class represents a Discord bot that uses a GPT-3 model to respond to messages.
    """

    def __init__(
        self,
        LLM_Data: dict,
        SD_Data: dict,
        channel_data: str,
        memory_size: int = 5,
        use_translator: bool = False,
    ):
        translator = None
        if use_translator:
            logging.info("Using translator...")
            translator = Translator()

        model_name = LLM_Data["model_name"]
        ollama_url = LLM_Data["ollama_url"]

        self.model = GeneralLLMModel(
            model_name,
            translator,
            prompt_path="prompts/base_prompt.txt",
            temp=0.9,
            ollama_url=ollama_url,
        )

        self.sd_llm_model = None
        self.sd_client = None
        if "url" in SD_Data and "checkpoint" in SD_Data:
            self.sd_llm_model = GeneralLLMModel(
                model_name,
                None,
                prompt_path="prompts/sd_prompt.txt",
                temp=0.9,
                ollama_url=ollama_url,
            )
            self.sd_client = SDClient(
                SD_Data["url"],
                SD_Data["checkpoint"],
                10,
                "prompts/sd_inverse_prompt.txt",
            )

        self.memories = MultiChannelMemory(
            memory_size=memory_size, load_path="memory.mem"
        )
        self.model_lock = False
        self.discord_commands = {
            "!change_status": change_status,
            "!clear": clear_memory,
            "!generate-image": generate_image,
        }
        self.ctx = {
            "sd_client": self.sd_client,
        }

        self.channel_data = channel_data

        self.memory_size = memory_size

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def _check_commands(self, message):
        while self.model_lock:
            logging.info("Waiting for model to unlock...")
            await asyncio.sleep(10)

        for command, func in self.discord_commands.items():
            if command in message.content:
                self.model_lock = True
                await func(self, command, message, self.ctx)
                self.model_lock = False
                return True
        return False

    async def _llm_response(self, message):
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
            response_message = await message.reply(response, mention_author=True)

            # Check for stable difussion
            if self.sd_client is not None:
                await self.check_for_image(response, response_message)

            self.memories.persist_memory()

        await asyncio.sleep(1)
        self.model_lock = False

    async def check_for_image(self, message_input: str, message: discord.Message):
        """
        Check if must generate an image.
        """
        response = await self.sd_llm_model.evaluate(message_input)
        logging.info("SD Response: %s", response)
        if "N/A" in response.upper() or len(response) < 5:
            return None

        file_name = await self.sd_client.txt2img(response)

        if file_name is None:
            return

        file = discord.File(file_name)
        await message.edit(attachments=[file])
        self.sd_client.delete_image(file_name)

    async def on_ready(self):
        """Called when the bot is ready."""
        logging.info("Bot %s is connected to server.", self.user.display_name)

    async def on_message(self, message):
        """Called when a message is sent in a channel the bot is in."""
        if message.author == self.user:
            return

        await manage_emojis_channel(message, self.channel_data["EMOJI_ONLY_CHANNELS"])

        if not is_valid_channel(message, self.channel_data["CHAT_CHANNELS"]):
            await message.reply("Sorry, I can't talk here.", mention_author=True)
            return

        await self._check_commands(message)

        if not self.user.mentioned_in(message):
            return

        await self._llm_response(message)
