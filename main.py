import os
from classes.discord_bot import LLamaBot
from dotenv import load_dotenv

load_dotenv()
TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")

if __name__ == "__main__":
    bot = LLamaBot()
    bot.run(TOKEN_DISCORD)
