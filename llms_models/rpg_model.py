import logging
from llms_models.llm_model import LLMModel


class RPGModel(LLMModel):
    def _generate_prompt(self, memory):
        prompt = super()._generate_prompt(memory)
        # TODO: Add the player stats to the prompt
        return prompt

    def evaluate_sync(self, initial_input_text, memory):
        input_text = self._translate_input(initial_input_text)

        memory.append_conversation(input_text)
        prompt = self._generate_prompt(memory)
        logging.debug("========= Prompt =========")
        logging.debug("Prompt: %s", prompt)
        logging.debug("==========================")

        output = self._generate_output(prompt)
        # self._clear_conversation_if_needed(output, initial_input_text, memory)

        # output = self._process_output(output, memory)
        memory.append_conversation(output.strip())
        output = self._translate_output(output)

        return output
