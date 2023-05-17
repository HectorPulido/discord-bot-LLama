import re
import os
import random
import discord
from discord.ext import tasks
from discord.ext.commands import Bot
from classes.llama_model import LlamaModel


class LLamaBot(Bot):
    def __init__(self):
        model_name = os.getenv("MODEL_NAME")
        self.llama_model = LlamaModel(model_name=model_name, temp=0.9)

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f"Bot {self.user.display_name} is connected to server.")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if "!change_status" in message.content:
            new_status = message.content.split("!change_status")[1]
            await self.change_presence(activity=discord.Game(name=new_status))

        if not self.user.mentioned_in(message):
            return

        message_text = str(message.content)
        message_text = re.sub(r"<@\d+>", "", message_text).strip()
        message_text = f"{message.author.display_name}: {message_text}"

        print(f"Message received: {message_text}")

        async with message.channel.typing():
            response = await self.llama_model.evaluate(message_text)
            await message.reply(response, mention_author=True)
            print(f"Response sent: {response}.")
