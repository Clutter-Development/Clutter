import os
from typing import TYPE_CHECKING

import json5

from .database import find_in_dict
from .errors import UnknownTranstaionString

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

    def translate_with_locale(self, locale: str, text: str, /) -> str:
        path = text.split(".")
        value = find_in_dict(self.languages[locale], path, default=find_in_dict(self.languages[self.fallback], path))
        if value is None:
            raise UnknownTranstaionString(f"Could not find translation for {text.join('.')}")
        return value

    async def __call__(self, ctx: discord.Message | discord.Interaction | commands.Context, text: str | list[str], /, *, use_guild: bool = False) -> str:
        is_interaction = isinstance(ctx, discord.Interaction)

        async def determine_guild_language() -> str:
            g_locale = ctx.guild_locale if is_interaction else ctx.guild.preferred_locale
            return await self._db.get(f"guilds.{ctx.guild.id}.language", default=g_locale or self.fallback)

        guild_exists = bool(ctx.guild_id if is_interaction else ctx.guild)

        if use_guild and guild_exists:
            lang = await determine_guild_language()
        else:
            user_locale = ctx.locale if is_interaction else None
            lang = await self._db.get(f"users.{ctx.user.id if is_interaction else ctx.author.id}.language", default=user_locale or await determine_guild_language())

        return self.translate_with_locale(lang, text)
