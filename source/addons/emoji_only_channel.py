"""
Emoji only channel manager
"""

import re


async def manage_emojis_channel(message):
    """
    Remove all discord emojis
    """

    message_content = message.content.lower()

    re_emoji = re.compile(r"<[^\s]+>")
    message_content = re_emoji.sub("", message_content)

    re_chars = re.compile(r"[a-z0-9\.\-=\*\&\^%\$\#@!`\~\?]")
    if re_chars.search(message_content):
        await message.delete()
