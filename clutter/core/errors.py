from __future__ import annotations

from discord import app_commands as app
from discord.ext import commands

__all__ = ("ClutterError", "UserIsBlacklisted", "UserHasBeenBlacklisted")


class ClutterError(app.AppCommandError, commands.CommandError):
    pass


class UserIsBlacklisted(ClutterError):
    pass


class UserHasBeenBlacklisted(ClutterError):
    pass
