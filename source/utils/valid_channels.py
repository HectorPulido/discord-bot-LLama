"""
Function to check if a message is in a valid channel.
"""

import re


def is_valid_channel(message, channels) -> bool:
    """
    Check if a message is in a valid channel.
    """
    if message.guild is None or message.channel is None:
        return False

    final_id = f"{message.guild.id}:{message.channel.id}"
    for channel in channels:
        if re.search(channel, final_id):
            return True

    return False
