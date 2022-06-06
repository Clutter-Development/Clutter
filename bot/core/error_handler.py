from __future__ import annotations

import asyncio
import traceback
from typing import TYPE_CHECKING

import color
import discord
import sentry_sdk
from discord import app_commands as app
from discord.ext import commands
from discord_utils import format_as_list, run_in_executor

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Clutter, /) -> None:
        self.bot = bot
        self.ignored_errors = (commands.CommandNotFound,)
        self.capture_exception = run_in_executor(sentry_sdk.capture_exception)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: ClutterContext, error: commands.CommandError, /
    ) -> None:
        if hasattr(ctx.command, "on_error"):
            return

        if cog := ctx.cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        error = getattr(error, "original", error)

        if isinstance(error, self.ignored_errors):
            return

        trace = traceback.format_exception(
            type(error), error, error.__traceback__
        )
        print(
            color.red(
                format_as_list(
                    f"An unhandled exception has occured in the command '{ctx.command.qualified_name}'",  # type: ignore
                    "\n".join(trace),
                )
            )
        )
        await asyncio.gather(
            self.capture_exception(error),
            self.bot.log_webhook.send(f"<@512640455834337290>```{trace}```"),
            ctx.reply_embed.error(
                ctx.i18n("ERROR.RESPONSE.TITLE"),
                ctx.i18n("ERROR.RESPONSE.BODY"),
            ),
        )

    @commands.Cog.listener()
    async def on_app_command_error(
        self, inter: discord.Interaction, error: app.AppCommandError, /
    ) -> None:
        pass


async def setup(bot: Clutter, /) -> None:
    await bot.add_cog(ErrorHandler(bot))
