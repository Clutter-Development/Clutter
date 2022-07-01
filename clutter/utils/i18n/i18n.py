from __future__ import annotations

from os import listdir, path
from typing import TYPE_CHECKING, Literal

from json5 import load

from .errors import NoFallback, UnknownTranslationCode
from .misc import find_in_nested_dict

if TYPE_CHECKING:
    from discord import Message
    from discord.ext.commands import Context

    from ...core.interaction import ClutterInteraction
    from ..db import CachedMongoManager

__all__ = ("I18N",)


class I18N:
    def __init__(
        self,
        lang_file_dir: str,
        *,
        db: CachedMongoManager,
        fallback_language: str,
    ) -> None:
        self._db = db
        self._languages = {}
        self._fallback_language = fallback_language

        files = listdir(lang_file_dir)

        for fn in files:
            if not fn.endswith(("json", "json5")):
                continue

            with open(path.join(lang_file_dir, fn)) as f:
                self._languages[fn.rsplit(".", 1)[0]] = load(f)

        if fallback_language not in self._languages:
            raise NoFallback(fallback_language, lang_file_dir)

    def collect_translations(self, code: str) -> dict[str, str]:
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
        *,
        object_type: Literal["guild", "user"] = "user",
    ) -> str:
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
        *,
        prefer_guild: bool = False,
    ) -> str:
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
