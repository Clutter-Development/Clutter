from discord import app_commands as app
from discord.ext import commands

__all__ = (
    "ClutterError",
    "BotInMaintenance",
    "UserIsBlacklisted",
    "UserHasBeenBlacklisted",
)


class ClutterError(app.AppCommandError, commands.CommandError):
    pass


class BotInMaintenance(ClutterError):
    pass


class UserIsBlacklisted(ClutterError):
    pass


class UserHasBeenBlacklisted(ClutterError):
    pass
