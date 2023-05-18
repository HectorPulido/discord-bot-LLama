import re
import os
import logging
import asyncio
import discord
from discord.ext.commands import Bot
from classes.llama_model import LlamaModel


class LLamaBot(Bot):
    def __init__(self):
        model_name = os.getenv("MODEL_NAME")
        self.model_lock = False

        self.model = LlamaModel(model_name=model_name, memory_size=1, temp=0.9)

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f"Bot {self.user.display_name} is connected to server.")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if "!change_status" in message.content:
            logging.info("Changing status...")
            new_status = message.content.split("!change_status")[1]
            await self.change_presence(activity=discord.Game(name=new_status))

        if not self.user.mentioned_in(message):
            return

        while self.model_lock:
            logging.info("Waiting for model to unlock...")
            await asyncio.sleep(1)

        message_text = str(message.content)
        message_text = re.sub(r"<@\d+>", "", message_text).strip()
        message_text = f"{message.author.display_name}: {message_text}"

        logging.info(f"Message received: {message_text}")

        async with message.channel.typing():
            self.model_lock = True
            response = await self.model.evaluate(message_text)
            logging.info(f"Response: {response}")
            await message.reply(response, mention_author=True)

        await asyncio.sleep(1)
        self.model_lock = False
