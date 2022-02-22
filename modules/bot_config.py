from discord.ext import commands

from utils.init import embed


class BotConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ALLOWED_KEYS = ["prefix", "emojis.success", "emojis.error", "emojis.warning", "emojis.info",
                             "colors.success", "colors.error", "colors.warning", "colors.info", "moderators.roles",
                             "moderators.users"]

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    async def config(self, ctx):
        pass

    @commands.command()
    async def set(self, ctx, key: str, value: str):
        if key not in self.ALLOWED_KEYS:
            return await ctx.reply(embed=embed.error(ctx.guild.id, "Invalid key provided",
                                                     f"To view the valid keys, execute `{self.bot.command_prefix}config valid_keys`"),
                                   mention_author=False)
        # TODO: make it work


def setup(bot):
    bot.add_cog(BotConfig(bot))
