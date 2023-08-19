import logging
from abc import ABC, abstractmethod
from utils import to_thread


class LLMModel(ABC):
    def __init__(
        self,
        llm_model,
        translator=None,
        prompt_path=None,
        prompt=None,
        **kwargs,
    ):
        self.kwargs = kwargs
        self.llm_model = llm_model
        self.translator = translator

        if prompt is not None and prompt_path is not None:
            raise ValueError("prompt and prompt_path cannot be set at the same time")

        if prompt_path is not None:
            with open(prompt_path, "r", encoding="utf-8") as file:
                self.prompt = file.read()

        if prompt is not None:
            self.prompt = prompt

        if prompt is None and prompt_path is None:
            self.prompt = "{input}"

    @to_thread
    def evaluate(self, initial_input_text, memory):
        return self.evaluate_sync(initial_input_text, memory)

    @abstractmethod
    def evaluate_sync(self, initial_input_text, memory):
        pass

    def _generate_prompt(self, memory):
        input_text = memory.historial_conversation()
        prompt = self.prompt.replace("{input}", input_text)
        return prompt

    def _split_user_input(self, input_text):
        user = ""
        if ": " in input_text:
            user, input_text = input_text.split(": ", 1)
        return user, input_text

    def _translate_input(self, initial_input_text):
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

    def _generate_output(self, prompt):
        while True:
            output = self.llm_model.generate(prompt, **self.kwargs)
            if len(output.strip()) > 0:
                logging.debug("Generated output: %s", output)
                return output
            logging.error("Generation failed, retrying...")

    def _translate_output(self, output):
        if self.translator is not None:
            translated_output = self.translator.english_to_spanish(output)
            if translated_output and translated_output != "":
                output = translated_output

        logging.debug("Final output processed: %s", output)
        return output
