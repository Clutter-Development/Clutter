from typing import Union

import discord
from discord.ext import commands


class BotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        pass

    @commands.command()
    async def moderators(self, ctx, operation_type: str, to_add: Union[discord.Member, discord.Role]):
        pass


def setup(bot):
    bot.add_cog(BotConfig(bot))
