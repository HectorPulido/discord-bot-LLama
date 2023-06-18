import re
import os
import logging
import asyncio
import discord
from discord.ext.commands import Bot
from discord.channel import TextChannel
from classes import LlamaModel, MemoryModel


class DiscordLLMBot(Bot):
    def __init__(self):
        model_name = os.getenv("MODEL_NAME")
        self.model_lock = False
        self.model = LlamaModel(model_name=model_name, temp=0.9)
        self.memories = {}

        self.discord_commands = {"!change_status": self._change_status}

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    def _get_memory(self, channel_id):
        if channel_id not in self.memories:
            self.memories[channel_id] = MemoryModel(memory_size=5)
        return self.memories[channel_id]

    async def _change_status(self, message):
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
        message_text = re.sub(r"<@\d+>", "", message_text).strip()
        message_text = f"{message.author.display_name}: {message_text}"

        logging.info("Message received in %s: %s", message.channel.id, message_text)

        async with message.channel.typing():
            self.model_lock = True
            memory = self._get_memory(message.channel.id)
            response = await self.model.evaluate(message_text, memory=memory)
            logging.info("Response: %s", response)
            await message.reply(response, mention_author=True)

        await asyncio.sleep(1)
        self.model_lock = False

    async def on_ready(self):
        print(f"Bot {self.user.display_name} is connected to server.")

    async def on_message(self, message):
        if message.author == self.user:
            return

        await self._check_commands(message)

        if not self.user.mentioned_in(message):
            return

        await self._llm_response(message)
