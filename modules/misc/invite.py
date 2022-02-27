from discord.ext import commands

from config import bot_info
from utils.init import embed


class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invite")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def _invite(self, ctx):
        await ctx.channel.trigger_typing()
        await ctx.reply(
            embed=embed.info(
                ctx.guild.id,
                "Invite me",
                f"[Bot invite]({bot_info['invite']})\n[Support server]({bot_info['discord']})",
            )
        )


def setup(bot):
    bot.add_cog(Invite(bot))