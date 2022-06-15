from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from discord.app_commands import AppCommandError, CommandTree

from .interaction import ClutterInteraction

if TYPE_CHECKING:
    from discord import Interaction
    from discord.app_commands import Command, ContextMenu, Group

    from .bot import ClutterBot

T = TypeVar("T")
CheckType = Callable[[ClutterInteraction], Awaitable[bool]]

__all__ = ("ClutterCommandTree",)


class ClutterCommandTree(CommandTree):
    bot: ClutterBot

    def __init__(self, bot: ClutterBot, /) -> None:
        super().__init__(bot)
        self.bot = self.client
        self.checks: list[CheckType] = []

    def add_command(
        self, command: Command | Group | ContextMenu, /, **kwargs
    ) -> None:
        # command.name = self.bot.i18n.collect_translations(command.description)
        # if not isinstance(command, ContextMenu):
        #     command.description = self.bot.i18n.collect_translations(command.description)
        # TODO: For when app command locales get implemented to discord.py.
        super().add_command(command, **kwargs)

    async def call(self, ctx: Interaction, /) -> None:
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
            except AppCommandError as e:
                await self.on_error(ctx, e)
                return False

        return True

    async def on_error(
        self, ctx: ClutterInteraction, error: AppCommandError, /
    ) -> None:
        self.bot.dispatch(
            "app_command_error", ctx, error
        )  # Rerouting to the error handler.
