from typing import Union

import discord
from discord.ext import commands

from utils.init import db, embed


class BotConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        pass

    @config.group(invoke_without_command=True, aliases=["moderator", "mod"])
    async def moderators(self, ctx):
        pass

    @moderators.command(name="add")
    async def _add(self, ctx, target: Union[discord.Member, discord.Role]):
        if isinstance(target, discord.Role):
            if str(target.id) in db.get(f"servers.{ctx.guild.id}.moderators.roles", []):
                return await ctx.send(
                    embed=embed.error(ctx.guild.id, f"**@{target.name}** is already a moderator role"),
                    mention_author=False)
            db.push(f"servers.{ctx.guild.id}.moderators.roles", str(target.id))
            return await ctx.send(embed=embed.success(ctx.guild.id, f"**@{target.name}** is now a moderator role"),
                                  mention_author=False)
        elif target.id in db.get(f"servers.{ctx.guild.id}.moderators.users", []):
            return await ctx.send(embed=embed.error(ctx.guild.id, f"**{target}** is already a moderator"),
                                  mention_author=False)
        db.push(f"servers.{ctx.guild.id}.moderators.users", str(target.id))
        await ctx.send(embed=embed.success(ctx.guild.id, f"**{target}** is now a moderator"), mention_author=False)

    @moderators.command(name="remove", alises=["rem"])
    async def _remove(self, ctx, target: Union[discord.Member, discord.Role]):
        if isinstance(target, discord.Role):
            if target.id not in db.get(f"servers.{ctx.guild.id}.moderators.roles", []):
                return await ctx.send(
                    embed=embed.error(ctx.guild.id, f"**@{target.name}** is already not a moderator role"),
                    mention_author=False)
            db.pull(f"servers.{ctx.guild.id}.moderators.roles", str(target.id))
            return await ctx.send(embed=embed.success(ctx.guild.id, f"**@{target.name}** is now not a moderator role"),
                                  mention_author=False)
        elif target.id not in db.get(f"servers.{ctx.guild.id}.moderators.users", []):
            return await ctx.send(embed=embed.error(ctx.guild.id, f"**{target}** is already not a moderator"),
                                  mention_author=False)
        db.pull(f"servers.{ctx.guild.id}.moderators.users", str(target.id))
        await ctx.send(embed=embed.success(ctx.guild.id, f"**{target}** is now not a moderator"),
                       mention_author=False)


def setup(bot):
    bot.add_cog(BotConfig(bot))
