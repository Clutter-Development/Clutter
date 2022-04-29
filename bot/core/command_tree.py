from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import discord
from discord import app_commands as app

if TYPE_CHECKING:
    from core.bot import Clutter

T = TypeVar("T")


class ClutterCommandTree(app.CommandTree):
    def __init__(self, bot: Clutter, /):
        """Initialize the ClutterCommandTree class.

        Args:
            bot (Clutter): The bot to use the command tree in.
        """
        super().__init__(bot)
        self.checks = []

    async def interaction_check(self, inter: discord.Interaction, /) -> bool:
        for check in self.checks:
            try:
                val = await check(inter)
            except app.AppCommandError as e:
                await self.on_error(inter, e)
                return False
            if val is False:
                return False
        return True

    def check(self, func: T) -> T:
        """Appends a check to the checks that get executed before every interaction

        Args:
            func (T): The check.

        Returns:
            T: The check.
        """
        self.checks.append(func)
        return func