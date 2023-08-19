import re
import logging
import asyncio
import discord
import gpt4all
from discord.ext.commands import Bot
from discord.channel import TextChannel

from memory import MultiChannelMemory
from translator import Translator
from llms_models import GeneralLLMModel


class DiscordLLMBot(Bot):
    def __init__(self, model_name, memory_size=5, use_translator=False):
        llm_model = gpt4all.GPT4All(model_name)

        translator = None
        if use_translator:
            logging.info("Using translator...")
            translator = Translator()

        self.model = GeneralLLMModel(
            llm_model, translator, prompt_path="prompts/base_prompt.txt", temp=0.9
        )
        self.memories = MultiChannelMemory(
            memory_size=memory_size, load_path="memory.mem"
        )
        self.model_lock = False
        self.discord_commands = {
            "!change_status": self._change_status,
            "!clear": self._clear_memory,
        }

        self.memory_size = memory_size

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def _clear_memory(self, message):
        if not message.author.guild_permissions.manage_messages:
            await message.reply(
                "You don't have permission to do that.", mention_author=True
            )
            return
        self.memories.clear_all_memory()
        await message.reply("Memory cleared.", mention_author=True)

    async def _change_status(self, message):
        if not message.author.guild_permissions.manage_messages:
            await message.reply(
                "You don't have permission to do that.", mention_author=True
            )
            return

        logging.info("Changing status...")
        new_status = message.content.split("!change_status")[1]
        await self.change_presence(activity=discord.Game(name=new_status))

    async def _check_commands(self, message):
        for command, func in self.discord_commands.items():
            if command in message.content:
                await func(message)
                return True
        return False

    async def _llm_response(self, message):
        if not isinstance(message.channel, TextChannel):
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

        if not self.user.mentioned_in(message):
            return

        await self._llm_response(message)
