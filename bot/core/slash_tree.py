from __future__ import annotations
import discord
from discord import app_commands as app
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from main import Clutter

T = TypeVar("T")


class ClutterCommandTree(app.CommandTree):
    def __init__(self, bot: Clutter, /):
        super().__init__(bot)
        self.checks = []

    def interaction_check(self, inter: discord.Interaction, /) -> bool:
        for check in self.checks:
            try:
                val = check(inter)
            except app.AppCommandError:
                return False
            if not val:
                return False
        return True

    def check(self, func: T) -> T:
        self.checks.append(func)
        return func
