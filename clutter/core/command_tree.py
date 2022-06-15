from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

import discord
from discord import app_commands as app

from .interaction import ClutterInteraction

if TYPE_CHECKING:
    from .bot import ClutterBot

T = TypeVar("T")
CheckType = Callable[[ClutterInteraction], Awaitable[bool]]


class ClutterCommandTree(app.CommandTree):
    bot: ClutterBot

    def __init__(self, bot: ClutterBot, /) -> None:
        super().__init__(bot)
        self.bot = self.client
        self.checks: list[CheckType] = []

    def add_command(
        self, command: app.Command | app.Group | app.ContextMenu, /, **kwargs
    ) -> None:
        # command.name = self.bot.i18n.collect_translations(command.description)
        # if not isinstance(command, app.ContextMenu):
        #     command.description = self.bot.i18n.collect_translations(command.description)
        # TODO: For when app command locales get implemented to discord.py.
        super().add_command(command, **kwargs)

    async def call(self, ctx: discord.Interaction, /) -> None:
        # Basically a 'custom' interaction class.
        await super().call(ClutterInteraction(ctx))  # type: ignore

    def check(self, func: CheckType) -> CheckType:
        self.checks.append(func)
        return func

    async def interaction_check(self, ctx: ClutterInteraction, /) -> bool:
        for check in self.checks:
            try:
                if not await check(ctx):
                    return False
            except app.AppCommandError as e:
                await self.on_error(ctx, e)
                return False

        return True

    async def on_error(
        self, ctx: ClutterInteraction, error: app.AppCommandError, /
    ) -> None:
        self.bot.dispatch(
            "app_command_error", ctx, error
        )  # Rerouting to the error handler.
