from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    import datetime

    import discord

    from ..utils import embed
    from .bot import ClutterBot

    class RespondEmbedCoroutine(Protocol):
        async def __call__(
            self,
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime.datetime | None = None,
            **kwargs: Any,
        ) -> None:
            ...


class RespondEmbedGetter:
    def __init__(
        self,
        ctx: ClutterInteraction,
        embed_creator: embed.EmbedCreator,
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
            timestamp: datetime.datetime | None = None,
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

    def __init__(self, ctx: discord.Interaction, /) -> None:
        self.__ctx = ctx
        self.bot = self.client
        self.author = self.user

    def __getattr__(self, item: str, /) -> Any:
        return getattr(self.__ctx, item)

    @property
    def respond_embed(self):
        return RespondEmbedGetter(self, self.bot.embed)

    async def i18n(self, text: str, /, *, use_guild: bool = False) -> str:
        return await self.bot.i18n(self, text, use_guild=use_guild)

    async def respond(self, *args, **kwargs) -> None:
        await self.response.send_message(*args, **kwargs)
