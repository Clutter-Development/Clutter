# from typing import Union

#import discord
from discord.ext import commands


#from utils.init import db, embed


class BotConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """@commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        await ctx.reply(
            embed=embed.error(ctx.guild.id, "You need to specify a sub command", "`moderators`"),
            mention_author=False,  # will make the valid subcmd list automated later
        )

    # Moderator Config
    @config.group(invoke_without_command=True, aliases=["moderator", "mod"])
    async def moderators(self, ctx):
        await ctx.reply(
            embed=embed.error(ctx.guild.id, "You need to specify a sub command", "`add` or `remove`"),
            mention_author=False,
        )

    @moderators.command(name="add")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def _add(self, ctx, target: Union[discord.Member, discord.Role]):
        if isinstance(target, discord.Role):
            if str(target.id) in db.get(f"servers.{ctx.guild.id}.moderators.roles", []):
                return await ctx.reply(
                    embed=embed.error(ctx.guild.id, f"**@{target.name}** is already a moderator role"),
                    mention_author=False,
                )
            db.push(f"servers.{ctx.guild.id}.moderators.roles", str(target.id))
            return await ctx.reply(
                embed=embed.success(ctx.guild.id, f"**@{target.name}** is now a moderator role"), mention_author=False
            )
        if str(target.id) in db.get(f"servers.{ctx.guild.id}.moderators.users", []):
            return await ctx.reply(
                embed=embed.error(ctx.guild.id, f"**{target}** is already a moderator"), mention_author=False
            )
        db.push(f"servers.{ctx.guild.id}.moderators.users", str(target.id))
        await ctx.reply(embed=embed.success(ctx.guild.id, f"**{target}** is now a moderator"), mention_author=False)

    @moderators.command(name="remove")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def _remove(self, ctx, target: Union[discord.Member, discord.Role]):
        if isinstance(target, discord.Role):
            if str(target.id) not in db.get(f"servers.{ctx.guild.id}.moderators.roles", []):
                return await ctx.reply(
                    embed=embed.error(ctx.guild.id, f"**@{target.name}** is already not a moderator role"),
                    mention_author=False,
                )
            db.pull(f"servers.{ctx.guild.id}.moderators.roles", str(target.id))
            return await ctx.reply(
                embed=embed.success(ctx.guild.id, f"**@{target.name}** is now not a moderator role"),
                mention_author=False,
            )
        elif str(target.id) not in db.get(f"servers.{ctx.guild.id}.moderators.users", []):
            return await ctx.reply(
                embed=embed.error(ctx.guild.id, f"**{target}** is already not a moderator"), mention_author=False
            )
        db.pull(f"servers.{ctx.guild.id}.moderators.users", str(target.id))
        await ctx.reply(embed=embed.success(ctx.guild.id, f"**{target}** is now not a moderator"), mention_author=False)"""


def setup(bot):
    bot.add_cog(BotConfig(bot))
