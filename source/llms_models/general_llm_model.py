"""
General class for LLM models.
"""

import logging
from llms_models.llm_model import LLMModel
from utils import to_thread


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

        if "generator" in kwargs:
            self.generator = kwargs["generator"]

    def _get_prompt(self, initial_input_text, memory=None):
        input_text = self._translate_input(initial_input_text)
        if memory:
            memory.append_conversation(input_text, "user")
            prompt = self._generate_prompt(memory)
        else:
            prompt = self._generate_bare_prompt(input_text)

        logging.debug("========= Prompt =========")
        logging.debug("Prompt: %s", prompt)
        logging.debug("==========================")

        return prompt

    def _post_process(self, output, initial_input_text, memory=None):
        if memory:
            self._clear_conversation_if_needed(output, initial_input_text, memory)
            output = self._process_output(output, memory)
            memory.append_conversation(f"Response: {output}", "assistant")

        output = self._translate_output(output)

        logging.debug("========= RESPONSE =========")
        logging.debug("RESPONSE: %s", output)
        logging.debug("==========================")

        return output

    async def evaluate_stream(self, initial_input_text, callback=None, memory=None):
        """
        Get the model's response to the input text.
        """
        async def ph_callback(output, force=False, iteration=0):
            pass

        if callback == None:
            callback = ph_callback


        prompt = self._get_prompt(initial_input_text, memory)

        stream = await self._generate_stream_output(prompt)
        output = ""
        iteration = 0

        for chunk in stream:
            iteration += 1
            output += chunk["message"]["content"]
            await callback(output, iteration=iteration)

        await callback(output, True)

        output = self._post_process(output, initial_input_text, memory)

        await callback(output, True)

        logging.debug(output)
        return output

    def evaluate_sync(self, initial_input_text, memory=None):
        """
        Get the model's response to the input text.
        """
        prompt = self._get_prompt(initial_input_text, memory)
        output = self._generate_output(prompt)
        output = self._post_process(output, initial_input_text, memory)

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
