"""
Discord client class.
"""

import re
import logging
import discord
from discord.ext.commands import Bot

from memory_models import MultiChannelMemory
from translator import Translator
from llms_models import GeneralLLMModel
from extra import clear_memory, change_status, manage_emojis_channel, generate_image
from utils import is_valid_channel, Lock
from sd_model import SDClient


class DiscordLLMBot(Bot):
    """
    This class represents a Discord bot that uses a GPT-3 model to respond to messages.
    """

    BASE_PROMPT_PATH = "prompts/base_prompt.txt"
    SD_PROMPT_PATH = "prompts/sd_prompt.txt"
    SD_INVERSE_PROMPT_PATH = "prompts/sd_inverse_prompt.txt"

    def __init__(
        self,
        llm_data: dict,
        sd_data: dict,
        channel_data: str,
        memory_size: int = 5,
        use_translator: bool = False,
    ):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.translator = Translator() if use_translator else None
        self.model = GeneralLLMModel(
            llm_data["model_name"],
            self.translator,
            prompt_path=self.BASE_PROMPT_PATH,
            temp=0.9,
            ollama_url=llm_data.get("ollama_url"),
            api_key=llm_data.get("api_key"),
        )

        # Initialize Stable Diffusion if data is provided
        self.sd_client = (
            SDClient(
                sd_data["url"], sd_data["checkpoint"], 10, self.SD_INVERSE_PROMPT_PATH
            )
            if sd_data.get("url") and sd_data.get("checkpoint")
            else None
        )

        self.sd_llm_model = (
            GeneralLLMModel(
                llm_data["model_name"],
                None,
                prompt_path=self.SD_PROMPT_PATH,
                temp=0.1,
                ollama_url=llm_data.get("ollama_url"),
            )
            if self.sd_client
            else None
        )

        self.memories = MultiChannelMemory(memory_size, "memory.mem")
        self.channel_data = channel_data

        # Context for command functions
        self.ctx = {"sd_client": self.sd_client}

        self.discord_commands = {
            "!change_status": change_status,
            "!clear": clear_memory,
            "!generate-image": generate_image,
        }

        self.model_lock = Lock(False)
        self.sd_lock = Lock(False)

    async def _check_commands(self, message):
        await self.model_lock.wait_lock()

        for command, func in self.discord_commands.items():
            if command in message.content:
                await self.model_lock.lock()
                await func(self, command, message, self.ctx)
                await self.model_lock.unlock()
                return True
        return False

    def _message_text_cleaner(self, message: discord.Message) -> str:
        message_text = str(message.content)
        message_text = re.sub(r"<@\d+>", "", message_text).strip()[-100:]
        message_text = f"{message.author.display_name}: {message_text}"
        return message_text

    def _edit_message_callback(self, message, max_iterations=5):
        async def message_callback(output, force=False, iteration=0):
            output_cleared = output.split("</think>")[-1][:3999]
            if "<think>" in output and "</think>" not in output:
                return
            if len(output_cleared) < 15:
                return
            if force or iteration % max_iterations == 0:
                await message.edit(content=output_cleared)

        return message_callback

    async def _llm_response(self, message):
        await self.model_lock.wait_lock()

        message_text = self._message_text_cleaner(message)

        logging.info("Message received in %s: %s", message.channel.id, message_text)

        async with message.channel.typing():
            await self.model_lock.lock()
            memory = self.memories.get_memory(message.channel.id)

            response_message = await message.reply("*Pensando...*", mention_author=True)
            callback = self._edit_message_callback(response_message)

            response = await self.model.evaluate_stream(
                message_text, callback, memory=memory
            )

            self.memories.persist_memory()
            await self.model_lock.unlock()

        # Check for stable difussion
        if self.sd_client is not None:
            await self.sd_lock.wait_lock()
            await self.sd_lock.lock()
            await self._check_for_image(message_text, response, response_message)
            await self.sd_lock.unlock()

    async def _check_for_image(
        self, message_input: str, message_output: str, message: discord.Message
    ):
        message_data = f"{message_input}\n{message_output}".replace(
            "<think>", "(think)"
        ).replace("</think>", "(/think)")

        response = await self.sd_llm_model.evaluate_stream(message_data)
        logging.info("SD Response: %s", response)
        if "N/A" in response.upper() or len(response) < 5:
            return None

        try:
            file_name = await self.sd_client.txt2img(response)
        except Exception as e:
            logging.error("Error generating image: %s", e)
            return

        if not file_name:
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
