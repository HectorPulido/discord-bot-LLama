"""
Script to use the bot in offline mode.
"""
import os
import logging
import gpt4all
from dotenv import load_dotenv
from translator import GeneralLLMModel, MemoryModel, Translator

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.offline.log",
    filemode="w",
    format="%(asctime)s -%(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

model_name = os.getenv("MODEL_NAME")
llm_model = gpt4all.GPT4All(model_name)
translator = Translator()

bot = GeneralLLMModel(
    llm_model, translator, prompt_path="prompts/base_prompt.txt", temp=0.9
)
memory = MemoryModel(memory_size=3)
print("Bot is starting...")
while True:
    prompt = input(">> ")
    response = bot.evaluate_sync("User: " + prompt, memory)
    print(f"bot: {response}")
