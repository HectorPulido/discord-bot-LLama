"""
This module contains various commands that can be executed by the bot.
It includes commands for changing the bot's status, generating images, etc.
"""

import logging
import discord


async def ping(_, message: discord.Message):
    """
    Responds with 'pong' to the user.
    """
    logging.info("Pong!")
    await message.reply("pong", mention_author=True)


async def change_status(bot, message):
    """
    Changes the bot's status.
    """
    if not message.author.guild_permissions.manage_messages:
        await message.reply(
            "You don't have permission to do that.", mention_author=True
        )
        return

    logging.info("Changing status...")
    new_status = message.content.split(message.content)[1]
    await bot.change_presence(activity=discord.Game(name=new_status))


async def generate_image(bot, message: discord.Message):
    """
    Generates an image based on the message.
    """

    if not bot.settings.use_stable_diffusion:
        await message.reply(
            "The bot is not configured to generate images.", mention_author=True
        )
        return

    logging.info("Generating image...")
    sd_client = bot.stable_diffusion_connection
    async with message.channel.typing():
        content = message.content.split(message.content)[1].strip()

        inverse_prompt = None
        if "|" in content:
            content, inverse_prompt = content.split("|")

        file_name = await sd_client.txt2img(content, inverse_prompt)
        if not file_name:
            return

        await message.reply(file=discord.File(file_name), mention_author=True)

        sd_client.delete_image(file_name)
