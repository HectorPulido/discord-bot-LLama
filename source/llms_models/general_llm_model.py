"""
General class for LLM models.
"""

import re
import logging
from llms_models.llm_model import LLMModel


class GeneralLLMModel(LLMModel):
    """
    Class for LLM models that don't require any special processing.
    """

    def __init__(
        self,
        llm_model: str,
        translator=None,
        prompt_path=None,
        prompt=None,
        **kwargs,
    ):
        super().__init__(
            llm_model,
            translator=translator,
            prompt_path=prompt_path,
            prompt=prompt,
            **kwargs,
        )

    def evaluate_sync(self, initial_input_text, memory):
        """
        Get the model's response to the input text.
        """
        input_text = self._translate_input(initial_input_text)

        memory.append_conversation(input_text, "user")
        prompt = self._generate_prompt(memory)
        logging.debug("========= Prompt =========")
        logging.debug("Prompt: %s", prompt)
        logging.debug("==========================")

        output = self._generate_output(prompt)
        self._clear_conversation_if_needed(output, initial_input_text, memory)

        output = self._process_output(output, memory)
        memory.append_conversation(f"Response: {output}", "assistant")
        output = self._translate_output(output)

        return output

    def _clear_conversation_if_needed(self, output, initial_input_text, memory):
        if output in [memory.get_last_response(), initial_input_text, ""]:
            memory.clear_conversation()
            logging.debug("Memory cleared...")

    def _process_output(self, output, memory):
        output = (
            output.replace("Response:", "")
            .replace("response:", "")
            .replace("RESPONSE:", "")
            .replace("Pequeñin:", "")
        )
        output = output.strip()

        memory.set_last_response(output)

        return output
