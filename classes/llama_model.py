import re
import logging
import gpt4all
from classes.translation import Translator
from classes.util import to_thread


class LlamaModel:
    def __init__(
        self,
        model_name="ggml-gpt4all-l13b-snoozy.bin",
        translate=True,
        memory_size=3,
        prompt_path="prompt_base.txt",
        prompt=None,
        **kwargs,
    ):
        self.kwargs = kwargs
        self.memory_size = memory_size
        self.conversation = []
        self.last_response = ""

        self.gptj = gpt4all.GPT4All(model_name)

        self.translate = translate
        if self.translate:
            self.translator = Translator()

        if prompt is not None and prompt_path is not None:
            raise ValueError("prompt and prompt_path cannot be set at the same time")

        if prompt_path is not None:
            with open("prompt_base.txt", "r", encoding="utf-8") as file:
                self.prompt = file.read()

        if prompt is not None:
            self.prompt = prompt

        if prompt is None and prompt_path is None:
            self.prompt = "{input}"

    def generate_prompt(self):
        prompt = self.prompt

        conversarion_min = []
        if len(self.conversation) < self.memory_size:
            conversarion_min = self.conversation
        else:
            conversarion_min = self.conversation[-self.memory_size :]

        input_text = "\n".join([f"> {i}" for i in conversarion_min])

        prompt = prompt.replace("{input}", input_text)

        return prompt

    @to_thread
    def evaluate(self, initial_input_text):
        return self.evaluate_sync(initial_input_text)

    def evaluate_sync(self, initial_input_text):
        input_text = self._translate_input(initial_input_text)

        self._append_conversation(input_text)
        prompt = self.generate_prompt()
        logging.debug("========= Prompt =========")
        logging.debug("Prompt: %s", prompt)
        logging.debug("==========================")

        output = self._generate_output(prompt)
        self._clear_conversation_if_needed(output, initial_input_text)

        output = self._process_output(output)
        self._append_conversation(f"Response: {output}")
        output = self._translate_output(output)

        return output

    def _translate_input(self, initial_input_text):
        if self.translate:
            initial_input_text = initial_input_text.strip()
            user, input_text = self._split_user_input(initial_input_text)
            input_text = self.translator.spanish_to_english(input_text)

            if user:
                input_text = f"{user}: {input_text}"

            logging.debug("Translated input: %s", input_text)
        else:
            input_text = initial_input_text

        return input_text

    def _split_user_input(self, input_text):
        user = ""
        if ": " in input_text:
            user, input_text = input_text.split(": ", 1)
        return user, input_text

    def _append_conversation(self, input_text):
        self.conversation.append(input_text)

    def _generate_output(self, prompt):
        output = self.gptj.generate(prompt, **self.kwargs)
        logging.debug("Generated output: %s", output)
        return output

    def _clear_conversation_if_needed(self, output, initial_input_text):
        if output in [self.last_response, initial_input_text]:
            self.conversation.clear()
        if output == "":
            self.conversation.clear()

    def _process_output(self, output):
        output = output.strip()
        output = re.split(r"\n+|#", output)[0].strip()
        output = output.replace(">", "")

        self.last_response = output

        return output

    def _translate_output(self, output):
        if self.translate:
            translated_output = self.translator.english_to_spanish(output)
            if translated_output and translated_output != "":
                output = translated_output

        logging.debug("Final output processed: %s", output)
        return output
