from __future__ import annotations

import os
from typing import TYPE_CHECKING

import json5

import discord
from .database import find_in_dict
from .errors import UnknownTranslationString
if TYPE_CHECKING:
    from discord.ext import commands
    from core.bot import Clutter


class I18N:
    def __init__(self, bot: Clutter, lang_file_dir: str, /):
        self._bot = bot
        self.languages = {}
        self.fallback = bot.default_language
        for lang_file in os.listdir(lang_file_dir):
            if lang_file.endswith(".json5"):
                with open(f"{lang_file_dir}/{lang_file}") as f:
                    self.languages[lang_file[:-6]] = json5.load(f)

    def translate_with_locale(self, language: str, text: str, /) -> str:
        """Translate a string with a locale. If the translation is not found, the fallback translation is used. If the fallback translation is not found, an error is raised.

        Args:
            language (str): The language to use.
            text (str): The string code to get translation of.

        Raises:
            UnknownTranslaionString: If the fallback translation is not found.

        Returns:
            str: The translated string.
        """
        path = text.split(".")
        value = find_in_dict(
            self.languages[language],
            path,
            default=find_in_dict(self.languages[self.fallback], path),
        )
        if value is None:
            raise UnknownTranslationString(f"Could not find translation for {text.join('.')}")
        return value

    async def __call__(
        self,
        ctx: discord.Message | discord.Interaction | commands.Context,
        text: str,
        /,
        *,
        use_guild: bool = False,
    ) -> str:
        """Translates a string code.

        Args:
            ctx (discord.Message | discord.Interaction | commands.Context): The language context to use.
            text (str | list[str]): The string code to get translation of.
            use_guild (bool, optional): To just use the guild language and ignoret the user's language. Defaults to False.

        Returns:
            str: The translated string.
        """
        is_interaction = isinstance(ctx, discord.Interaction)

        async def determine_guild_language() -> discord.Locale:
            if (is_interaction and not ctx.guild_id) or (not is_interaction and not ctx.guild):  # type: ignore
                return self.fallback
            g_locale = ctx.guild_locale if is_interaction else ctx.guild.preferred_locale  # type: ignore
            return await self._bot.db.get(
                f"guilds.{ctx.guild_id if is_interaction else ctx.guild.id}.language",  # type: ignore
                default=g_locale or self.fallback
            )

        guild_exists = bool(ctx.guild_id if is_interaction else ctx.guild)

        if use_guild and guild_exists:
            lang = await determine_guild_language()
        else:
            user_locale = ctx.locale if is_interaction else None
            lang = await self._bot.db.get(
                f"users.{ctx.user.id if is_interaction else ctx.author.id}.language",
                default=user_locale or await determine_guild_language(),
            )
        lang = lang.value
        if lang not in self.languages:
            lang = self.fallback

        return self.translate_with_locale(lang, text)
