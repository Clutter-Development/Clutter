from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

import discord
from discord import app_commands as app

if TYPE_CHECKING:
    from core.bot import Clutter

__all__ = ("ClutterCommandTree",)

T = TypeVar("T")


class ClutterCommandTree(app.CommandTree):
    client: Clutter

    def __init__(self, bot: Clutter, /) -> None:
        super().__init__(bot)
        self.checks: list[Callable[[discord.Interaction], Awaitable[bool]]] = []

    def add_command(
        self, command: app.Command | app.Group | app.ContextMenu, /, **kwargs
    ) -> None:
        # if not isinstance(command, app.ContextMenu):
        #     command.description = self.client.i18n.collect_translations(command.description)
        # TODO: For when app command locales get implemented to discord.py.
        super().add_command(command, **kwargs)

    def check(self, func: T) -> T:
        self.checks.append(func)
        return func

    async def interaction_check(self, inter: discord.Interaction, /) -> bool:
        for check in self.checks:
            try:
                if not await check(inter):
                    return False
            except app.AppCommandError as e:
                await self.on_error(inter, e)
                return False

        return True

    async def on_error(
        self, inter: discord.Interaction, error: app.AppCommandError, /
    ) -> None:
        self.client.dispatch(
            "app_command_error", inter, error
        )  # Rerouting to the error handler.
