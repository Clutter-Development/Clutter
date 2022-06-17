from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal

from json5 import load

from .errors import NoFallback, UnknownTranslationCode
from .misc import find_in_nested_dict

if TYPE_CHECKING:
    from discord import Message
    from discord.ext.commands import Context
    from mongo_manager import CachedMongoManager

    from ...core.interaction import ClutterInteraction

__all__ = ("I18N",)


class I18N:
    def __init__(
        self,
        language_file_directory: str,
        /,
        *,
        db: CachedMongoManager,
        fallback_language: str,
    ) -> None:
        """Initialize the I18N class.

        Args:
            language_file_directory (str): The directory that has all the translations. The file names must be the language the file houses.
            db (MongoManager): The database to use. The languages of the users should be "users.{id}.language" and the language of the guilds should be "guild.{id}.language".
            fallback_language (str): The fallback language to use if the translation string doesn't exist in the user/guilds language.
        """
        self._db = db
        self._languages = {}
        self._fallback_language = fallback_language

        files = os.listdir(language_file_directory)

        for fn in files:
            if not fn.endswith(("json", "json5")):
                continue

            with open(os.path.join(language_file_directory, fn)) as f:
                self._languages[fn.rsplit(".", 1)[0]] = load(f)

        if fallback_language not in self._languages:
            raise NoFallback(fallback_language, language_file_directory)

    def collect_translations(self, code: str, /) -> dict[str, str]:
        """Gets all translations of a string and returns a dict of translations.

        Args:
            code (str): The translation code to get the translations of.

        Returns:
            dict[str, str]: All translations of the translation code.
        """
        return {
            language: translation
            for language, translation in map(
                lambda kv: (kv[0], find_in_nested_dict(kv[1], code)),
                self._languages.items(),
            )
            if translation
        }

    async def translate_with_id(
        self,
        object_id: int,
        code: str,
        /,
        *,
        object_type: Literal["guild", "user"] = "user",
    ) -> str:
        """Fetches the preferred language using the id and type. Then gets the translation with the language.
        If the translation is not found, the fallback translation is used. If the fallback translation is not found, an error is raised.

        Args:
            object_id (int): The target id.
            code (str): The translation code to get translation of.
            object_type ("guild" | "user", optional): The id's type. Defaults to "user".

        Raises:
            UnknownTranslaionCode: If the fallback translation is not found and self._invalid_code is None.

        Returns:
            str: The translated string.
        """
        translated = find_in_nested_dict(
            self._languages.get(
                await self._db.get(
                    f"{object_type}s.{object_id}.language",
                    default=self._fallback_language,
                ),
                self._fallback_language,
            ),
            code,
            default=find_in_nested_dict(
                self._languages[self._fallback_language],
                code,
            ),
        )
        if not translated:
            raise UnknownTranslationCode(code)

        return translated

    async def __call__(
        self,
        ctx: Message | Context | ClutterInteraction,
        code: str,
        /,
        *,
        prefer_guild: bool = False,
    ) -> str:
        """Gets the corresponding translation for the translation code.

        Args:
            ctx (discord.Message | commands.Context | ClutterIntreraction): The object whose preffered language to get the translation of the translation code.
            code (str): The translation code to get translation of.
            prefer_guild (bool, optional): Whether to use the guild's language or the user's language. Defaults to False.

        Raises:
            UnknownTranslationCode: Raised if the translation of the translation code doesn't exist both in the preffered language and the fallback language and self._invalid_code is None.

        Returns:
            str: The translation corresponding to the translation code.
        """
        return (
            await self.translate_with_id(
                ctx.guild.id,  # type: ignore
                code,
                object_type="guild",
            )
            if prefer_guild
            else await self.translate_with_id(
                ctx.author.id, code, object_type="user"
            )
        )
