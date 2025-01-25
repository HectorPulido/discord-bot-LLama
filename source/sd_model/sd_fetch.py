"""
Client for the automatic1111 model.
"""

import os
import base64
import json
import random
import logging
import requests

from utils import to_thread


class SDClient:
    """
    Client for the automatic1111 model.
    """

    def __init__(
        self, url: str, sd_checkpoint: str, steps: int, negative_prompt_path: str = None
    ):
        self.url = f"{url}/sdapi/v1/txt2img"
        self.sd_checkpoint = sd_checkpoint
        self.steps = steps

        self.negative_prompt = ""
        if negative_prompt_path is not None:
            self.negative_prompt = self.load_prompt(negative_prompt_path)

    def delete_image(self, file_name: str):
        """
        Delete the image file.
        """

        if not (
            file_name.startswith("output_")
            and file_name.endswith(".png")
            and os.path.exists(file_name)
        ):
            return
        os.remove(file_name)
        logging.info("Image deleted: %s", file_name)

    def load_prompt(self, prompt_path: str) -> str:
        """
        Load the prompt from a text.
        """
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    @to_thread
    def txt2img(self, prompt: str, inverse_prompt: str = None) -> str:
        """
        Generate an image from a text prompt.
        """

        if inverse_prompt is None:
            inverse_prompt = self.negative_prompt

        logging.info(
            "generating image... prompt: %s, inverse_prompt: %s",
            prompt,
            inverse_prompt,
        )
        prompt = prompt.split('</think>')[-1]
        payload = json.dumps(
            {
                "prompt": prompt,
                "negative_prompt": inverse_prompt,
                "steps": self.steps,
                "override_settings": {
                    "sd_model_checkpoint": self.sd_checkpoint,
                },
            }
        )
        headers = {"Content-Type": "application/json"}

        # 5 mins
        timeout = 60 * 10
        response = requests.request(
            "POST", self.url, headers=headers, data=payload, timeout=timeout
        )

        if response.status_code != 200:
            logging.error("Error generating image: %s", response.text)
            return ""

        r = response.json()

        # Decode and save the image.
        random_number = random.randint(0, 100000)
        file_name = f"output_{random_number}.png"
        with open(file_name, "wb") as f:
            f.write(base64.b64decode(r["images"][0]))

        logging.info("Image generated: %s", file_name)
        return file_name
