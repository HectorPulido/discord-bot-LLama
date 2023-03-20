import torch
from peft import PeftModel
from transformers import LlamaTokenizer, LlamaForCausalLM, GenerationConfig

from classes.translation import Translator
from classes.util import to_thread


class LlamaModel:
    def __init__(
        self,
        temperature=0.1,
        top_p=0.75,
        num_beams=4,
        max_new_tokens=255,
        translate=True,
        memory_size=5,
    ):
        llama_7b_hf = "decapoda-research/llama-7b-hf"
        alpaca_lora_7b = "tloen/alpaca-lora-7b"

        self.memory_size = memory_size
        self.conversation = []
        self.last_response = ""

        self.tokenizer = LlamaTokenizer.from_pretrained(llama_7b_hf)

        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
            if torch.backends.mps.is_available():
                self.device = "mps"

        if self.device == "cuda":
            model = LlamaForCausalLM.from_pretrained(
                llama_7b_hf,
                load_in_8bit=True,
                torch_dtype=torch.float16,
                device_map="auto",
            )
            self.model = PeftModel.from_pretrained(
                model, alpaca_lora_7b, torch_dtype=torch.float16
            )
        elif self.device == "mps":
            model = LlamaForCausalLM.from_pretrained(
                llama_7b_hf,
                device_map={"": self.device},
                torch_dtype=torch.float16,
            )
            self.model = PeftModel.from_pretrained(
                model,
                alpaca_lora_7b,
                device_map={"": self.device},
                torch_dtype=torch.float16,
            )
        else:
            model = LlamaForCausalLM.from_pretrained(
                llama_7b_hf, device_map={"": self.device}, low_cpu_mem_usage=True
            )
            self.model = PeftModel.from_pretrained(
                model,
                alpaca_lora_7b,
                device_map={"": self.device},
            )

        self.generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            num_beams=num_beams,
        )

        self.max_new_tokens = max_new_tokens

        self.translate = translate
        if self.translate:
            self.translator = Translator()

        with open("prompt_base.txt", "r", encoding="utf-8") as f:
            self.prompt = f.read()

    def generate_prompt(self, instruction):
        prompt = self.prompt

        conversarion_min = []
        if len(self.conversation) < self.memory_size:
            conversarion_min = self.conversation
        else:
            conversarion_min = self.conversation[-self.memory_size :]

        input_text = ""
        for i in conversarion_min:
            input_text += f"### {i}\n\n"

        prompt = prompt.replace("{instruction}", instruction)
        prompt = prompt.replace("{input}", input_text)

        return prompt

    @to_thread
    def evaluate(self, instruction, initial_input_text):
        if self.translate:
            instruction = self.translator.spanish_to_english(instruction)
            input_text = self.translator.spanish_to_english(initial_input_text)
        else:
            input_text = initial_input_text

        self.conversation.append(input_text)

        prompt = self.generate_prompt(instruction)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.device)

        with torch.no_grad():
            generation_output = self.model.generate(
                input_ids=input_ids,
                generation_config=self.generation_config,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=self.max_new_tokens,
            )
        sequence = generation_output.sequences[0]
        output = self.tokenizer.decode(sequence)
        output = output.split("### Response:")[1].strip()

        self.conversation.append(f"Me: {output}")

        if output in [self.last_response, initial_input_text]:
            self.conversation.clear()
        self.last_response = output

        if self.translate:
            output = self.translator.english_to_spanish(output)
        return output
