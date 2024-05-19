import logging
import discord
from sd_model import SDClient


async def clear_memory(bot, _, message, __):
    """
    Clears the bot's memory.
    """
    if not message.author.guild_permissions.manage_messages:
        await message.reply(
            "You don't have permission to do that.", mention_author=True
        )
        return
    bot.memories.clear_all_memory()
    await message.reply("Memory cleared.", mention_author=True)


async def change_status(bot, command, message, _):
    """
    Changes the bot's status.
    """
    if not message.author.guild_permissions.manage_messages:
        await message.reply(
            "You don't have permission to do that.", mention_author=True
        )
        return

    logging.info("Changing status...")
    new_status = message.content.split(command)[1]
    await bot.change_presence(activity=discord.Game(name=new_status))


async def generate_image(_, command, message, ctx):
    """
    Generates an image based on the message.
    """

    if "sd_client" not in ctx:
        await message.reply(
            "The bot is not configured to generate images.", mention_author=True
        )
        return

    logging.info("Generating image...")
    sd_client = ctx["sd_client"]

    async with message.channel.typing():
        content = message.content.split(command)[1].strip()

        inverse_prompt = None
        if "|" in content:
            content, inverse_prompt = content.split("|")

        file_name = await sd_client.txt2img(content, inverse_prompt)

        await message.reply(file=discord.File(file_name), mention_author=True)

        sd_client.delete_image(file_name)
