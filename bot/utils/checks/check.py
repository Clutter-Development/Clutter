from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from discord import Interaction
    from discord import app_commands as app

    from ..database import CachedMongoManager

__all__ = ("CommandChecks",)


class CommandChecks:
    def __init__(self, db: CachedMongoManager, /):
        self._db = db

    @staticmethod
    def bot_admin_only() -> Callable:
        async def predicate(inter: Interaction, /) -> bool:
            return inter.user.id in inter.client.admin_ids  # type: ignore

        return app.check(predicate)

    @staticmethod
    def cooldown(rate: float, per: float, /) -> Callable:
        async def predicate(inter: Interaction, /) -> Optional[app.Cooldown]:
            if inter.user.id in inter.client.admin_ids:  # type: ignore
                return None
            return app.Cooldown(rate, per)

        return app.checks.dynamic_cooldown(predicate)
