"""
Client for the AUTOMATIC1111 Stable Diffusion Web UI (txt2img endpoint).

Notes on this refactor:
- Logic is preserved; only readability and documentation are improved.
- Added type hints, constants, and clearer variable names.
- Comments and docstrings are in English.
"""

import base64
import json
import logging
import os
import random
import functools
import typing
import asyncio

from typing import Any, Dict, Optional

import requests


def to_thread(func: typing.Callable):
    """
    Function to run sync functions in a thread pool.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


class SDClient:
    """Thin client around AUTOMATIC1111's `/sdapi/v1/txt2img` endpoint.

    Parameters
    ----------
    url : str
        Base URL of the AUTOMATIC1111 server (without the endpoint path).
    sd_checkpoint : str
        Name or identifier of the SD checkpoint to load (as in Web UI).
    steps : int
        Default number of sampling steps to use when not specified in payload.
    negative_prompt_path : str | None, optional
        Path to a text file containing a default negative prompt. If provided,
        it will be used when `inverse_prompt` is not passed to `txt2img`.
    """

    # Endpoint path appended to the provided base URL.
    TXT2IMG_PATH = "/sdapi/v1/txt2img"

    # File naming pattern and simple safeguards used by delete_image.
    OUTPUT_PREFIX = "output_"
    OUTPUT_SUFFIX = ".png"

    # HTTP timeout in seconds (10 minutes). Kept as in original logic.
    DEFAULT_TIMEOUT_SECONDS = 60 * 10

    def __init__(
        self,
        url: str,
        sd_checkpoint: str,
        steps: int,
        negative_prompt_path: Optional[str] = None,
    ) -> None:
        self.url = f"{url}{self.TXT2IMG_PATH}"
        self.sd_checkpoint = sd_checkpoint
        self.steps = steps

        self.negative_prompt: str = ""
        if negative_prompt_path is not None:
            self.negative_prompt = self.load_prompt(negative_prompt_path)

    # ---------------------------------------------------------------------
    # Filesystem helpers
    # ---------------------------------------------------------------------
    def delete_image(self, file_name: str) -> None:
        """Delete a previously generated image file if it matches our pattern.

        This is a safety check to avoid deleting arbitrary files.
        """
        if not (
            file_name.startswith(self.OUTPUT_PREFIX)
            and file_name.endswith(self.OUTPUT_SUFFIX)
            and os.path.exists(file_name)
        ):
            return

        os.remove(file_name)
        logging.info("Image deleted: %s", file_name)

    def load_prompt(self, prompt_path: str) -> str:
        """Load a prompt from a UTF-8 encoded text file and return it as a string."""
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    # ---------------------------------------------------------------------
    # Generation
    # ---------------------------------------------------------------------
    @to_thread
    def txt2img(self, prompt: str, inverse_prompt: Optional[str] = None) -> str:
        """Generate an image from a text prompt.

        The `prompt` may be either a plaintext prompt or a JSON string with
        full AUTOMATIC1111 payload. If JSON is provided, we respect it and only
        ensure the checkpoint and steps are set according to this client.

        Returns
        -------
        str
            Filename of the generated PNG on success, or an empty string on error.
        """
        is_json = False
        json_payload: Optional[Dict[str, Any]] = None

        # Try to detect a JSON-based prompt.
        try:
            json_payload = json.loads(prompt)
            is_json = True
            logging.info("prompt is json")
        except json.JSONDecodeError:
            is_json = False
            logging.info("prompt is plain text")

        # Default negative prompt if none provided at call time.
        if inverse_prompt is None:
            inverse_prompt = self.negative_prompt

        logging.info(
            "generating image... prompt: %s, inverse_prompt: %s",
            prompt,
            inverse_prompt,
        )

        # Build payload either from provided JSON or from plaintext prompt.
        if is_json and json_payload is not None:
            # Ensure checkpoint and steps are consistent with client config.
            json_payload["override_settings"] = {
                "sd_model_checkpoint": self.sd_checkpoint,
            }
            if "steps" in json_payload:
                json_payload["steps"] = min(
                    self.steps, json_payload["steps"]
                )  # keep original behavior
            else:
                json_payload["steps"] = self.steps
            payload = json.dumps(json_payload)
        else:
            # Drop any hidden-thought prefix if present and keep the visible tail.
            visible_prompt = prompt.split("</think>")[-1]
            payload = json.dumps(
                {
                    "prompt": visible_prompt,
                    "negative_prompt": inverse_prompt,
                    "steps": self.steps,
                    "override_settings": {
                        "sd_model_checkpoint": self.sd_checkpoint,
                    },
                }
            )

        headers = {"Content-Type": "application/json"}

        # Keep the same effective timeout as the original implementation (10 minutes).
        timeout_seconds = self.DEFAULT_TIMEOUT_SECONDS
        try:
            response = requests.request(
                "POST", self.url, headers=headers, data=payload, timeout=timeout_seconds
            )
        except Exception as e:
            logging.error("HTTP request failed: %s", e)
            return ""

        if response.status_code != 200:
            logging.error("Error generating image: %s", response.text)
            return ""

        # Decode image and persist to disk with a random filename.
        try:
            data = response.json()
            random_number = random.randint(0, 100000)
            file_name = f"{self.OUTPUT_PREFIX}{random_number}{self.OUTPUT_SUFFIX}"
            with open(file_name, "wb") as f:
                f.write(base64.b64decode(data["images"][0]))
        except Exception as e:
            logging.error("Error decoding image: %s", e)
            return ""

        logging.info("Image generated: %s", file_name)
        return file_name
