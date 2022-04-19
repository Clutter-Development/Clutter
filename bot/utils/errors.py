import discord
from discord import app_commands as app

__all__ = ("ClutterError", "InDevelopmentMode", "UserBlacklisted", "GuildBlacklisted")


class ClutterError(discord.DiscordException):
    """Base class for all Clutter errors."""

    pass


class InDevelopmentMode(ClutterError, app.AppCommandError):
    """Raised when a user is not a bot admin and bot is in development mode when using an app command."""

    pass


class UserBlacklisted(ClutterError, app.AppCommandError):
    """Raised when a user is blacklisted when using an app command."""

    pass


class GuildBlacklisted(ClutterError, app.AppCommandError):
    """Raised when a guild is blacklisted when using an app command."""

    pass
