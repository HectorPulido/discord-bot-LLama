import re
import discord
from discord.ext import commands
from classes.llama_model import LlamaModel


class LLamaBot(commands.Bot):
    def __init__(self):
        with open("instructions.txt", "r", encoding="utf-8") as f:
            instruction = f.read()
        self.instruction = instruction
        self.llama_model = LlamaModel()

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f"Bot {self.user.display_name} is connected to server.")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if not self.user.mentioned_in(message):
            return

        message_text = str(message.content)
        message_text = re.sub(r"<@\d+>", "", message_text).strip()
        message_text = f"{message.author.display_name}: {message_text}"

        print(f"Message received: {message_text}")

        async with message.channel.typing():
            response = await self.llama_model.evaluate(self.instruction, message_text)
            await message.reply(response, mention_author=True)
            print(f"Response sent: {response}.")
