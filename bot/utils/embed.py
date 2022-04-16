from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from discord import Embed

if TYPE_CHECKING:
    from .database.cacher import CachedMongoManager

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, config: dict, db: CachedMongoManager, /) -> None:
        self._config = config
        self._db = db
        self._embeds = []
        self.success = self._assemble_embed("SUCCESS")
        self.error = self._assemble_embed("ERROR")
        self.warning = self._assemble_embed("WARNING")
        self.info = self._assemble_embed("INFO")
        self.check_configuration()

    def _assemble_embed(self, asset_type: str, /) -> Callable:
        """Makes a function that returns an embed with the given asset type.

        Args:
            asset_type (str): The asset type to use.
        """

        async def create_embed(guild_id: int, title: str, description: str, /) -> Embed:
            """Creates an embed with the colors and emojis from the server configuration.

            Args:
                guild_id (int): The guild ID to get the configuration from.
                title (str): The title of the embed.
                description (str): The description of the embed.
            """
            nonlocal asset_type
            emoji = await self._db.get(
                f"guilds.{guild_id}.emojis.{asset_type.lower()}", default=self._config["EMOJIS"][asset_type]
            )
            color = await self._db.get(
                f"guilds.{guild_id}.colors.{asset_type.lower()}", default=self._config["COLORS"][asset_type]
            )
            return Embed(title=f"{emoji} {title}", description=description, color=color)

        self._embeds.append(asset_type)
        return create_embed

    async def create_embed(self, asset_type: str, guild_id: int, title: str, description: str, /) -> Embed:
        """Basically self._assemble_embed() but in one function"""
        return await self._assemble_embed(asset_type)(guild_id, title, description)

    def check_configuration(self) -> None:
        """Checks if the configuration is valid.

        Raises:
            KeyError: If a key is missing from the configuration.
        """
        for asset_type in self._embeds:
            if asset_type not in self._config["EMOJIS"] and asset_type not in self._config["COLORS"]:
                raise KeyError("Needed embed asset type not found in configuration.")
