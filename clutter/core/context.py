from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from discord.ext.commands import Context

if TYPE_CHECKING:
    from datetime import datetime

    from discord import Message

    from ..utils.embed import EmbedCreator
    from .bot import ClutterBot

    class ReplyEmbedCoroutine(Protocol):
        async def __call__(
            self,
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime | None = None,
            **kwargs: Any,
        ) -> Message:
            ...


__all__ = ("ClutterContext",)


class ReplyEmbedGetter:
    def __init__(
        self, ctx: ClutterContext, embed_creator: EmbedCreator, /
    ) -> None:
        self.__ctx = ctx
        self.__embed_creator = embed_creator

    def __getattr__(self, item: str) -> ReplyEmbedCoroutine:
        async def runner(
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime | None = None,
            **kwargs: Any,
        ) -> Message:
            return await self.__ctx.reply(
                embed=self.__embed_creator.__call__(
                    item, title, description, url=url, timestamp=timestamp
                ),
                **kwargs,
            )

        return runner


class ClutterContext(Context):
    bot: ClutterBot

    @property
    def reply_embed(self) -> ReplyEmbedGetter:
        return ReplyEmbedGetter(self, self.bot.embed)

    async def i18n(self, text: str, /, *, use_guild: bool = False, **kwargs: Any) -> str:
        return (await self.bot.i18n(self, text, use_guild=use_guild)).format(**kwargs)

    async def ok(self, value: bool, /) -> None:
        emojis = self.bot.config["STYLE"]["EMOJIS"]
        await self.message.add_reaction(emojis["SUCCESS" if value else "ERROR"])
