from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import discord

if TYPE_CHECKING:
    from discord import Interaction
    from discord import app_commands as app

    from ..main import Clutter

__all__ = ("CommandChecks",)


class CommandChecks:
    def __init__(self, bot: Clutter, /):
        self._bot = bot

    def cooldown(self, rate: float, per: float, /) -> Callable[[discord.Interaction], Optional[app.Cooldown]]:
        """Adds a cooldown to a command. Bypasses the cooldown if the user is a bot admin."""

        async def predicate(inter: Interaction, /) -> Optional[app.Cooldown]:
            if inter.user.id in self._bot.admin_ids:
                return None
            return app.Cooldown(rate, per)

        return app.checks.dynamic_cooldown(predicate)
