import gpt4all
from classes.translation import Translator
from classes.util import to_thread


class LlamaModel:
    def __init__(
        self,
        model_name="ggml-gpt4all-l13b-snoozy.bin",
        translate=True,
        memory_size=3,
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

        with open("prompt_base.txt", "r", encoding="utf-8") as file:
            self.prompt = file.read()

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
        if self.translate:
            input_text = self.translator.spanish_to_english(initial_input_text)
        else:
            input_text = initial_input_text

        self.conversation.append(input_text)

        prompt = self.generate_prompt()
        print(prompt)
        output = self.gptj.generate(prompt, **self.kwargs)

        self.conversation.append(f"Me: {output}")

        if output in [self.last_response, initial_input_text]:
            self.conversation.clear()
        self.last_response = output

        if self.translate:
            output = self.translator.english_to_spanish(output)
        return output.strip().split("\n")[0]
