import math
import sys
import traceback

import discord
from discord.ext import commands

from config import secrets
from utils.init import chalk, embed, mktxt


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
        ignored = (commands.CommandNotFound, commands.DisabledCommand, commands.NoPrivateMessage)
        error = getattr(error, "original", error)
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.BotMissingPermissions):
            missing = "\n".join([f"`{perm}`" for perm in error.missing_permissions])
            try:
                await ctx.trigger_typing()
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
        await ctx.trigger_typing()
        if isinstance(error, commands.CommandOnCooldown):
            usable_after = math.ceil(error.retry_after)
            await ctx.reply(
                embed=embed.error(
                    ctx.guild.id,
                    "This command is on cooldown",
                    f"You can use this command again in {usable_after} second{'s' if usable_after != 1 else ''}",
                )
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                embed=embed.error(
                    ctx.guild.id, "Please fill all the required arguments", f"Missing the argument `{error.param}`"
                ),
                mention_author=False,
            )
        elif isinstance(error, (commands.CheckFailure, commands.CheckAnyFailure)):
            await ctx.reply(embed=embed.error(ctx.guild.id, "You cannot use this command"), mention_author=False)
        else:
            full_error = f"\nIgnoring exception in command {ctx.command}:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}"
            print(
                chalk.red(full_error),
                file=sys.stderr,
            )
            await ctx.reply(
                embed=embed.error(
                    ctx.guild.id, "An unexpected error occured", "The bot developers have been notified to fix this bug"
                ),
                mention_author=False,
            )
            webhook = discord.SyncWebhook.from_url(secrets["error_webhook"])
            webhook.send(
                f"@everyone Error from the server '{ctx.guild.name}'",
                username="Error Log",
                file=mktxt(full_error, "error"),
            )


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
