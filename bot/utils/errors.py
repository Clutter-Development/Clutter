import discord
from discord import app_commands as app

__all__ = (
    "ClutterError",
    "InDevelopmentMode",
    "UserIsBlacklisted",
    "GuildIsBlacklisted",
    "UserHasBeenBlacklisted",
    "GlobalCooldownReached",
    "UnknownTranslationString",
)


class ClutterError(discord.DiscordException):
    """Base class for all Clutter errors."""


class InDevelopmentMode(ClutterError, app.AppCommandError):
    """Raised when a user is not a bot admin and bot is in development mode when using an app command."""


class UserIsBlacklisted(ClutterError, app.AppCommandError):
    """Raised when a user is blacklisted when using an app command."""


class GuildIsBlacklisted(ClutterError, app.AppCommandError):
    """Raised when a guild is blacklisted when using an app command."""


class UserHasBeenBlacklisted(ClutterError, app.AppCommandError):
    """Raised when a user is blacklisted when using an app command."""


class GlobalCooldownReached(ClutterError, app.AppCommandError):
    """Raised when a user is blacklisted when using an app command."""

    def __init__(self, retry_after: float, message: str, /):
        self.retry_after = retry_after
        self.message = message

    def __str__(self):
        return self.message


class UnknownTranslationString(ClutterError, app.AppCommandError):
    """Raised when a translation string is missing"""
