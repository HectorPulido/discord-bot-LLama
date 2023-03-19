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
    ):
        llama_7b_hf = "decapoda-research/llama-7b-hf"
        alpaca_lora_7b = "tloen/alpaca-lora-7b"
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

    def generate_prompt(self, instruction, input):
        with open("prompt_base.txt", "r") as f:
            prompt = f.read()
        prompt = prompt.replace("{instruction}", instruction)
        prompt = prompt.replace("{input}", input)
        return prompt

    @to_thread
    def evaluate(self, instruction, input_text):
        if self.translate:
            instruction = self.translator.spanish_to_english(instruction)
            input_text = self.translator.spanish_to_english(input_text)

        prompt = self.generate_prompt(instruction, input_text)
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
        s = generation_output.sequences[0]
        output = self.tokenizer.decode(s)
        output = output.split("### Response:")[1].strip()

        if self.translate:
            output = self.translator.english_to_spanish(output)
        return output
