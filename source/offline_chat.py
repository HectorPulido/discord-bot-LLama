"""
Script to use the bot in offline mode.
"""

import os
import logging
from dotenv import load_dotenv
from memory_models import MemoryModel
from translator import Translator
from llms_models import GeneralLLMModel

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.offline.log",
    filemode="w",
    format="%(asctime)s -%(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

model_name = os.getenv("MODEL_NAME")
translator = Translator()

bot = GeneralLLMModel("gemma:2b", None, prompt_path="prompts/base_prompt.txt", temp=0.9)
memory = MemoryModel(memory_size=3)
print("Bot is starting...")
while True:
    prompt = input(">> ")
    response = bot.evaluate_sync("User: " + prompt, memory)
    print(f"bot: {response}")
