from typing import Optional, Tuple

import discord
from discord.ext import commands


class ClutterContext(commands.Context):
    async def reply_embed(self, asset_type: str, title: str, description: Optional[str] = None, /) -> discord.Message:
        return await self.reply(embed=self.bot.embed(asset_type, title, description))

    async def ok(self, value: bool, /) -> None:
        emojis = self.bot.config["STYLE"]["EMOJIS"]
        return await self.message.add_reaction(emojis["SUCCESS" if value else "ERROR"])

    async def maybe_dm_embed(
        self, asset_type: str, title: str, description: Optional[str] = None, /
    ) -> Tuple[Optional[discord.Message], bool]:
        try:
            return await self.author.send(embed=self.bot.embed(asset_type, title, description)), True
        except (discord.Forbidden, discord.HTTPException):
            return None, False
