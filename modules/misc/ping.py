from discord.ext import commands

from utils.init import embed


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="ping")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def _ping(self, ctx):
        await ctx.reply(
            embed=embed.info(ctx.guild.id, f"Pong! `{round(self.bot.latency * 1000)}ms`"), mention_author=False
        )


def setup(bot):
    bot.add_cog(Ping(bot))
