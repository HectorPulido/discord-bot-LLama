import os
from dotenv import load_dotenv
from classes.llama_model import LlamaModel

load_dotenv()

model_name = os.getenv("MODEL_NAME")

if __name__ == "__main__":
    bot = LlamaModel(model_name=model_name, temp=0.9)
    print("Bot is starting...")
    while True:
        prompt = input(">> ")
        response = bot.evaluate_sync("User: " + prompt)
        print(f"bot: {response}")
