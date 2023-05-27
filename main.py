import os
import logging
from classes.discord_bot import LLamaBot
from dotenv import load_dotenv

load_dotenv()
TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",
    filemode="w",
    format="%(asctime)s -%(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

if __name__ == "__main__":
    bot = LLamaBot()
    bot.run(TOKEN_DISCORD)
