from __future__ import annotations

import asyncio
import traceback
from typing import TYPE_CHECKING

import color
import sentry_sdk
from discord import app_commands as app
from discord.ext import commands
from discord_utils import TextFile, format_as_list, run_in_executor

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext
    from core.interaction import ClutterInteraction


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Clutter, /) -> None:
        self.bot = bot
        self.capture_exception = run_in_executor(sentry_sdk.capture_exception)

    async def handle_error(
        self, ctx: ClutterContext | ClutterInteraction, error: Exception, /
    ) -> None:
        trace = traceback.format_exception(
            type(error), error, error.__traceback__
        )
        print(
            color.red(
                format_as_list(
                    f"An unhandled exception has occured in the command '{ctx.command.qualified_name}'",
                    "\n".join(trace),
                )
            )
        )
        if guild := ctx.guild:
            head = f"Error from the server {guild.name} with the ID {guild.id}."
        else:
            author = ctx.author
            head = f"Error from the DMs with the user {author} with the ID {author.id}."

        await asyncio.gather(
            self.capture_exception(error),
            self.bot.log_webhook.send(
                file=TextFile(
                    f"{head}\nCommand: {ctx.command.qualified_name}\nTraceback:\n{trace}"
                )
            ),
            ctx.reply_embed.error(
                await ctx.i18n("ERROR.RESPONSE.TITLE"),
                await ctx.i18n("ERROR.RESPONSE.BODY"),
            ),
        )

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: ClutterContext, error: commands.CommandError, /
    ) -> None:
        error = getattr(error, "original", error)

        match error:
            case commands.CommandNotFound():
                return

            case _:
                await self.handle_error(ctx, error)

    @commands.Cog.listener()
    async def on_app_command_error(
        self, inter: ClutterInteraction, error: app.AppCommandError, /
    ) -> None:
        error = getattr(error, "original", error)

        match error:
            case _:
                await self.handle_error(inter, error)


async def setup(bot: Clutter, /) -> None:
    await bot.add_cog(ErrorHandler(bot))
