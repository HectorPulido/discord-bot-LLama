"""
Emoji only channel manager
"""
import re
from utils import is_valid_channel


async def manage_emojis_channel(message, channels):
    """
    Remove all discord emojis
    """
    if not is_valid_channel(message, channels):
        return

    message_content = message.content.lower()

    re_emoji = re.compile(r"<[^\s]+>")
    message_content = re_emoji.sub("", message_content)

    re_chars = re.compile(r"[a-z0-9\.\-=\*\&\^%\$\#@!`\~\?]")
    if re_chars.search(message_content):
        await message.delete()
