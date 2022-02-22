"""
Why like this? Can't you make a callable generator?
I tried, but it didn't work. It bugged hard. Python moment.
"""
import discord

from config import defaults


class Embed:

    def __init__(self, db) -> None:
        self.db = db

    def _assemble_embed(self, *, asset_type: str, guild_id: int, title: str, description: str = "") -> discord.Embed:
        return discord.Embed(
            title=f"{self.db.get(f'servers.{guild_id}.emojis.{asset_type}', defaults['emojis'][asset_type])} {title}",
            description=description,
            color=self.db.get(f"servers.{guild_id}.colors.{asset_type}", defaults["colors"][asset_type]))

    def success(self, guild_id: int, title: str, description: str = "") -> discord.Embed:
        return self._assemble_embed(asset_type="success", guild_id=guild_id, title=title, description=description)

    def error(self, guild_id: int, title: str, description: str = "") -> discord.Embed:
        return self._assemble_embed(asset_type="error", guild_id=guild_id, title=title, description=description)

    def warning(self, guild_id: int, title: str, description: str = "") -> discord.Embed:
        return self._assemble_embed(asset_type="warning", guild_id=guild_id, title=title, description=description)

    def info(self, guild_id: int, title: str, description: str = "") -> discord.Embed:
        return self._assemble_embed(asset_type="info", guild_id=guild_id, title=title, description=description)
