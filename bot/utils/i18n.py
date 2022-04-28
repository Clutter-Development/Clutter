"""import os
from typing import TYPE_CHECKING

import json5

if TYPE_CHECKING:
    import discord
    from discord.ext import commands
    from core.bot import Clutter


class I18N:
    def __init__(self, bot: Clutter, lang_file_dir: str, /, *, fallback: str = "en-US"):
        self._db = bot.db
        self.languages = {}
        self.fallback = fallback
        for lang_file in os.listdir(lang_file_dir):
            if lang_file.endswith(".json5"):
                with open(os.path.join(lang_file_dir, lang_file)) as f:
                    self.languages[lang_file[:-6]] = json5.load(f)

    async def __call__(self, ctx: discord.Message | discord.Interaction | commands.Context, text: str | list[str], /, *,
                       use_guild: bool = False) -> str:
        is_inter = isinstance(ctx, discord.Interaction)

        def get_guild_lang() -> str:
            return await self._db.get(f"guilds.{ctx.guild_id if is_inter else ctx.guild.id}.language",
                                      default=ctx.guild_locale if is_inter else ctx.guild.preferred_locale) or self.fallback

        if use_guild:
            language = get_guild_lang()
        else:
            language = await self._db.get(f"users.{ctx.author.id}.language", default=ctx.locale if is_inter else get_guild_lang())"""
