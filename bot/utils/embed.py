from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed

if TYPE_CHECKING:
    from .database.cacher import CachedMongoManager


class EmbedBuilder:
    def __init__(self, db: CachedMongoManager, /) -> None:
        self._db = db
        self.success = self._assemble_embed("success")
        self.error = self._assemble_embed("error")
        self.warning = self._assemble_embed("warning")
        self.info = self._assemble_embed("info")

    def _assemble_embed(self, asset_type: str, /):  # FIXME TODO: type this
        async def create_embed(guild_id: int, title: str, description: str, /) -> Embed:
            nonlocal asset_type
            doc = await self._db.get(f"guilds.{guild_id}.responses")
            emoji = doc["emojis"][asset_type]
            color = doc["colors"][asset_type]
            return Embed(title=f"{emoji} {title}", description=description, color=color)

        return create_embed
