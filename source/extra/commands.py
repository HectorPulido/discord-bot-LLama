import logging
import discord


async def clear_memory(self, message):
    if not message.author.guild_permissions.manage_messages:
        await message.reply(
            "You don't have permission to do that.", mention_author=True
        )
        return
    self.memories.clear_all_memory()
    await message.reply("Memory cleared.", mention_author=True)


async def change_status(self, message):
    if not message.author.guild_permissions.manage_messages:
        await message.reply(
            "You don't have permission to do that.", mention_author=True
        )
        return

    logging.info("Changing status...")
    new_status = message.content.split("!change_status")[1]
    await self.change_presence(activity=discord.Game(name=new_status))
