import discord
from discord import app_commands as app

__all__ = ("ClutterError", "InDevelopmentMode", "Blacklisted")


class ClutterError(discord.DiscordException):
    """Base class for all Clutter errors."""

    pass


class InDevelopmentMode(ClutterError, app.AppCommandError):
    """Raised when a user is not a bot admin and bot is in development mode when using an app command."""

    pass


class Blacklisted(ClutterError, app.AppCommandError):
    """Raised when a user is blacklisted when using an app command."""

    pass
