"""
This module provides a StreamEditor class for managing the streaming of chat messages
and editing a reply message in a Discord bot context. It handles the buffering of
streamed chunks, sanitizes the visible content, and edits the reply message at specified intervals.
"""

import logging
import discord
from core.rate_limit import Throttle


class StreamEditor:
    """
    StreamEditor manages the streaming of chat messages and edits a reply message in Discord.
    It buffers incoming chunks, sanitizes the visible content, and edits the reply message
    at specified intervals or when forced.
    """

    def __init__(
        self,
        message: discord.Message,
        *,
        safe_edit_length: int,
        edit_every_n_chunks: int,
        edit_min_interval_ms: int,
    ):
        self.message = message
        self.safe_edit_length = safe_edit_length
        self.every = edit_every_n_chunks
        self.iteration = 0
        self.buffer = ""
        self._throttle = Throttle(edit_min_interval_ms)
        self.reply_message: discord.Message | None = None

    def _sanitize_visible(self, output: str) -> str:
        visible = output.split("</think>")[-1]
        if "<think>" in output and "</think>" not in output:
            return ""
        return visible

    async def on_stream_chunk(self, chunk: str, *, force: bool = False):
        """
        Processes a chunk of streamed content, updates the buffer, and edits the reply message
        if conditions are met.
        """
        self.iteration += 1
        self.buffer += chunk
        visible = self._sanitize_visible(self.buffer)

        if not self.reply_message:
            self.reply_message = await self.message.reply("Thinking...")

        if force or (self.iteration % self.every == 0 and await self._throttle.ready()):
            try:
                await self.reply_message.edit(content=visible)
            except Exception as e:
                logging.error("Error editing message (force): %s", e)
            return
