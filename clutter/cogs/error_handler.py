from __future__ import annotations

import logging as log
from asyncio import gather
from traceback import format_exception
from typing import TYPE_CHECKING

from discord.app_commands import AppCommandError
from discord.ext.commands import Cog, CommandError, CommandNotFound
from sentry_sdk import capture_exception

from ..utils import TextFile, color, format_as_list, run_in_executor

if TYPE_CHECKING:
    from ..core import ClutterBot, ClutterContext, ClutterInteraction


class ErrorHandler(Cog):
    def __init__(self, bot: ClutterBot) -> None:
        self.bot = bot
        self.capture_exception = run_in_executor(capture_exception)

    async def handle_error(
        self,
        ctx: ClutterContext | ClutterInteraction,
        error: Exception,
    ) -> None:
        traceback = format_exception(type(error), error, error.__traceback__)

        log.error(
            color.red(
                format_as_list(
                    f"An unhandled exception has occured in the command '{ctx.command.qualified_name}'",  # type: ignore
                    "\n".join(traceback),
                )
            )
        )

        if ctx.guild:
            head = (
                f"Error from the server {ctx.guild.name} with the ID"
                f" {ctx.guild.id}."
            )
        else:
            head = (
                f"Error from the DMs with the user {ctx.author} with the ID"
                f" {ctx.author.id}."
            )

        await gather(
            self.capture_exception(error),
            self.bot.error_webhook.send(
                file=TextFile(
                    f"{head}\nCommand: {ctx.command.qualified_name}\nTraceback:\n{traceback}",  # type: ignore
                    "error.txt",
                )
            ),
            ctx.reply_embed.error(
                await ctx.i18n("ERROR.RESPONSE.TITLE"),
                await ctx.i18n("ERROR.RESPONSE.BODY"),
            ),
        )

    @Cog.listener()
    async def on_command_error(
        self, ctx: ClutterContext, error: CommandError
    ) -> None:
        error = getattr(error, "original", error)

        match error:
            case CommandNotFound():
                return

            case _:
                await self.handle_error(ctx, error)

    @Cog.listener()
    async def on_app_command_error(
        self, ctx: ClutterInteraction, error: AppCommandError
    ) -> None:
        error = getattr(error, "original", error)

        match error:
            case _:
                await self.handle_error(ctx, error)


async def setup(bot: ClutterBot) -> None:
    await bot.add_cog(ErrorHandler(bot))
