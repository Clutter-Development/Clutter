from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import discord
from discord import app_commands as app

if TYPE_CHECKING:
    from core.bot import Clutter

T = TypeVar("T")


class ClutterCommandTree(app.CommandTree):
    def __init__(self, bot: Clutter, /) -> None:
        super().__init__(bot)
        self.checks = []

    async def interaction_check(self, inter: discord.Interaction, /) -> bool:
        for check in self.checks:
            try:
                await check(inter)
                return True
            except app.AppCommandError as e:
                await self.on_error(inter, e)
                return False

    def check(self, func: T) -> T:
        self.checks.append(func)
        return func
