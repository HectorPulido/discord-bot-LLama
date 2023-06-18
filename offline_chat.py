import os
from dotenv import load_dotenv
from classes import LlamaModel, MemoryModel

load_dotenv()

model_name = os.getenv("MODEL_NAME")

if __name__ == "__main__":
    bot = LlamaModel(model_name=model_name, temp=0.9)
    memory = MemoryModel(memory_size=3)
    print("Bot is starting...")
    while True:
        prompt = input(">> ")
        response = bot.evaluate_sync("User: " + prompt, memory)
        print(f"bot: {response}")
