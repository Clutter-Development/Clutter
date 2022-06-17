from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from datetime import datetime

    from discord import Interaction

    from ..utils.embed import EmbedCreator
    from .bot import ClutterBot

    class RespondEmbedCoroutine(Protocol):
        async def __call__(
            self,
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime | None = None,
            **kwargs: Any,
        ) -> None:
            ...


__all__ = ("ClutterInteraction",)


class RespondEmbedGetter:
    def __init__(
        self,
        ctx: ClutterInteraction,
        embed_creator: EmbedCreator,
        /,
    ) -> None:
        self.__ctx = ctx
        self.__embed_creator = embed_creator

    def __getattr__(self, item: str) -> RespondEmbedCoroutine:
        async def runner(
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime | None = None,
            **kwargs: Any,
        ) -> None:
            await self.__ctx.respond(
                embed=self.__embed_creator(
                    item, title, description, url=url, timestamp=timestamp
                ),
                **kwargs,
            )

        return runner


class ClutterInteraction:
    bot: ClutterBot

    def __init__(self, ctx: Interaction, /) -> None:
        self.__ctx = ctx
        self.bot = self.client
        self.author = self.user

    def __getattr__(self, item: str, /) -> Any:
        return getattr(self.__ctx, item)

    @property
    def reply_embed(self) -> RespondEmbedGetter:
        return RespondEmbedGetter(self, self.bot.embed)

    async def i18n(
        self, text: str, /, *, prefer_guild: bool = False, **kwargs: str
    ) -> str:
        return (await self.bot.i18n(self, text, prefer_guild=prefer_guild)).format(
            **kwargs
        )

    async def reply(self, *args: Any, **kwargs: Any) -> None:
        await self.response.send_message(*args, **kwargs)
