import datetime
import platform
import time

from discord.ext import commands

from config import bot_info
from utils.init import embed


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global start_time
        start_time = round(time.time())

    @commands.command(name="info", aliases=["botinfo", "about", "stats", "uptime"])
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def _info(self, ctx):
        _embed = embed.info(ctx.guild.id, "Bot Info")
        _embed.add_field(name="Total Guilds", value=f"```{len(self.bot.guilds)}```")
        _embed.add_field(name="Total Members", value=f"```{len(self.bot.users)}```")
        _embed.add_field(name="Bot Version", value=f"```{bot_info['version']}```")
        _embed.add_field(name="Python Version", value=f"```v{platform.python_version()}```")
        _embed.add_field(name="Uptime", value=f"```{datetime.timedelta(seconds=round(time.time()) - start_time)}```")

        await ctx.reply(embed=_embed, mention_author=False)


def setup(bot):
    bot.add_cog(Info(bot))
