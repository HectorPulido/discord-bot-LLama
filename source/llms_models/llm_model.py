"""
Base class for LLM models
"""

import logging
from abc import ABC, abstractmethod

from ollama import Client
import ollama

from utils import to_thread
from memory_models import MemoryModel


class LLMModel(ABC):
    """
    Base class for LLM models

    Args:
        llm_model (str): The LLM model to use
        **kwargs: Additional arguments for the model

        Possible kwargs:
            - translator: A translator object to translate the input and output
            - option: A specific option for the model
            - prompt: The prompt to use (if prompt_path is not set)
            - prompt_path: The path to the prompt file (if prompt is not set)

    """

    def __init__(
        self,
        llm_model: str,
        **kwargs,
    ):
        self.kwargs = kwargs
        self.llm_model = llm_model

        self.translator = self.kwargs.get("translator", None)
        self.option = self.kwargs.get("option", None)
        self.ollama_url = self.kwargs.get("ollama_url", None)

        if self.ollama_url is not None:
            self.client_ollama = Client(host=self.ollama_url)
        else:
            self.client_ollama = ollama

        self.client_ollama.pull(self.llm_model)

        if (
            "prompt" in kwargs
            and kwargs["prompt"] is not None
            and "prompt_path" in kwargs
            and kwargs["prompt_path"] is not None
        ):
            raise ValueError("prompt and prompt_path cannot be set at the same time")

        self.prompt = None
        if "prompt_path" in kwargs and kwargs["prompt_path"] is not None:
            prompt_path = kwargs["prompt_path"]
            with open(prompt_path, "r", encoding="utf-8") as file:
                self.prompt = file.read()

        if "prompt" in kwargs and kwargs["prompt"] is not None:
            prompt = kwargs.get("prompt", None)
            self.prompt = prompt

    @to_thread
    def evaluate(self, initial_input_text: str, memory: MemoryModel = None) -> str:
        """
        get the response from the model
        """
        return self.evaluate_sync(initial_input_text, memory)

    @abstractmethod
    def evaluate_sync(self, initial_input_text: str, memory: MemoryModel = None) -> str:
        """
        abstract method for getting the response from the model
        """

    def _generate_bare_prompt(self, input_text: str):
        return [
            {
                "role": "system",
                "content": self.prompt,
            },
            {
                "role": "user",
                "content": input_text,
            },
        ]

    def _generate_prompt(self, memory: MemoryModel):
        conversation = memory.historial_conversation()

        if self.prompt is not None:
            conversation = [
                {
                    "role": "system",
                    "content": self.prompt,
                }
            ] + conversation
        return conversation

    def _generate_output(self, prompt):
        try:
            response = self.client_ollama.chat(
                model=self.llm_model,
                options=self.option,
                messages=prompt,
            )
            output = response["message"]["content"]
            logging.debug("Generated output: %s", output)
            return output
        except Exception as e:
            logging.error("Error generating output: %s", e)
            return ""

    def _split_user_input(self, input_text: str):
        user = ""
        if ": " in input_text:
            user, input_text = input_text.split(": ", 1)
        return user, input_text

    def _translate_input(self, initial_input_text: str) -> str:
        if self.translator is not None:
            initial_input_text = initial_input_text.strip()
            user, input_text = self._split_user_input(initial_input_text)
            input_text = self.translator.spanish_to_english(input_text)

            if user:
                input_text = f"{user}: {input_text}"

            logging.debug("Translated input: %s", input_text)
        else:
            input_text = initial_input_text

        return input_text

    def _translate_output(self, output: str) -> str:
        if self.translator is not None:
            translated_output = self.translator.english_to_spanish(output)
            if translated_output and translated_output != "":
                output = translated_output

        logging.debug("Final output processed: %s", output)
        return output
