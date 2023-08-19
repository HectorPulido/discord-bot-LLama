"""
Entry point of the application.
"""

import os
import logging
from dotenv import load_dotenv
from discord_client import DiscordLLMBot


load_dotenv()
TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
MODEL_NAME = os.getenv("MODEL_NAME")
MEMORY_SIZE = int(os.getenv("MEMORY_SIZE"))
TRANSLATOR = bool(os.getenv("TRANSLATOR"))

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",
    filemode="w",
    format="%(asctime)s -%(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

if __name__ == "__main__":
    bot = DiscordLLMBot(MODEL_NAME, MEMORY_SIZE, TRANSLATOR)
    bot.run(TOKEN_DISCORD)
