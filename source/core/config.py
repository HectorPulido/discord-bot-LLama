"""
This module provides configuration settings for the Discord bot and OpenAI API.
It uses environment variables to set various parameters such as the Discord token,
OpenAI API key, model, and other operational settings.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """
    Configuration settings for the Discord bot and OpenAI API.
    """

    discord_token: str = os.getenv("DISCORD_TOKEN", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    max_context_messages: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "15"))
    edit_every_n_chunks: int = int(os.getenv("EDIT_EVERY_N_CHUNKS", "15"))
    min_message_length: int = int(os.getenv("MIN_MESSAGE_LENGTH", "20"))
    safe_edit_length: int = int(os.getenv("SAFE_EDIT_LENGTH", "1000"))
    edit_min_interval_ms: int = int(os.getenv("EDIT_MIN_INTERVAL_MS", "500"))
    mention_required: bool = os.getenv("MENTION_REQUIRED", "false").lower() == "true"
    chat_channels: str = os.getenv("CHAT_CHANNELS", "")
    emoji_only_channels: str = os.getenv("EMOJI_ONLY_CHANNELS", "")
    base_prompt_path: str = os.getenv("BASE_PROMPT_PATH", "default")
    sd_checkpoint: str | None = os.getenv("SD_CHECKPOINT", None)
    sd_url: str | None = os.getenv("SD_URL", None)

    def __init__(self, **kwargs):
        """
        Initialize the Settings object with provided keyword arguments.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Process the chat channels and emoji-only channels
        self.chat_channels_data = (
            self.chat_channels.split(",") if self.chat_channels else []
        )
        self.emoji_only_channels_data = (
            self.emoji_only_channels.split(",") if self.emoji_only_channels else []
        )

        # Load the base prompt from the specified file or use a default prompt
        if os.path.exists(self.base_prompt_path):
            with open(self.base_prompt_path, "r", encoding="utf-8") as file:
                self.base_prompt = file.read()
        else:
            self.base_prompt = (
                "You are a helpful assistant. Please answer"
                "the questions based on the context provided."
            )

        # Determine if Stable Diffusion is enabled
        self.use_stable_diffusion = self.sd_url is not None and self.sd_url != ""

    @staticmethod
    def get_settings() -> "Settings":
        """
        Retrieves the settings for the application from environment variables.
        """
        return Settings()
