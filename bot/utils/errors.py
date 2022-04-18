import discord
from discord import app_commands as app

__all__ = ("ClutterError", "NotAnAdmin", "Blacklisted")


class ClutterError(discord.DiscordException):
    """Base class for all Clutter errors."""

    pass


class NotAnAdmin(app.AppCommandError):
    """Raised when a user is not a bot admin when using an app command."""

    pass


class Blacklisted(app.AppCommandError):
    """Raised when a user is blacklisted when using an app command."""

    pass
