from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Union

from discord import Embed

if TYPE_CHECKING:
    from .database.cacher import CachedMongoManager

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, config: Dict[str, Union[int, Dict[str, Union[str, int]]]], db: CachedMongoManager, /) -> None:
        self._config = config
        self._db = db
        self.success = self._assemble_embed("success")
        self.error = self._assemble_embed("error")
        self.warning = self._assemble_embed("warning")
        self.info = self._assemble_embed("info")

    def _assemble_embed(self, asset_type: str, /):  # FIXME TODO: type this
        async def create_embed(guild_id: int, title: str, description: str, /) -> Embed:
            nonlocal asset_type
            emoji = await self._db.get(f"guilds.{guild_id}.emojis.{asset_type}", default=self._config["emojis"][asset_type])
            color = await self._db.get(f"guilds.{guild_id}.colors.{asset_type}", default=self._config["colors"][asset_type])
            return Embed(title=f"{emoji} {title}", description=description, color=color)

        return create_embed
