import logging
import discord


async def clear_memory(bot, message):
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
    new_status = message.content.split("!change_status")[1]
    await bot.change_presence(activity=discord.Game(name=new_status))
