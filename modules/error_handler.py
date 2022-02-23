import sys
import traceback

import discord
# from discord import Webhook
# from discord.webhook.async_ import AsyncWebhookAdapter
# import aiohttp
from discord.ext import commands

# from config import secrets
from utils.init import chalk, embed  # , get_txt


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return
        if cog := ctx.cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound, commands.DisabledCommand)
        error = getattr(error, "original", error)
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                embed=embed.error(ctx.guild.id, "Please fill all the required arguments"), mention_author=False
            )
        elif isinstance(error, (commands.CheckFailure, commands.CheckAnyFailure)):
            await ctx.reply(embed=embed.error(ctx.guild.id, "You cannot use this command"), mention_author=False)
        elif isinstance(error, commands.BotMissingPermissions):
            missing = "\n".join([f"`{perm}`" for perm in error.missing_permissions])
            try:
                await ctx.reply(
                    embed=embed.error(
                        ctx.guild.id,
                        "I don't have the required permissions to do this",
                        f"Missing the following permissions:\n{missing}",
                    ),
                    mention_author=False,
                )
            except (discord.Forbidden, discord.HTTPException):
                pass
        else:
            print(
                chalk.red(
                    f"\nIgnoring exception in command {ctx.command}:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}"
                ),
                file=sys.stderr,
            )
            await ctx.reply(
                embed=embed.error(
                    ctx.guild.id, "An unexpected error occured", "The bot developers have been notified to fix this bug"
                ),
                mention_author=False,
            )
            # async with aiohttp.ClientSession() as session:
            #    webhook = Webhook.from_url(secrets["error_webhook"], AsyncWebhookAdapter())
            # TODO: Add error webhook, this doesnt work, pycord moment


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
