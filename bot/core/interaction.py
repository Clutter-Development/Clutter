from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    import datetime

    import discord
    from core.bot import Clutter
    from discord_utils import QuickEmbedCreator

    class ReplyEmbedCoroutine(Protocol):
        async def __call__(
            self,
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime.datetime | None = None,
            **kwargs: Any,
        ) -> discord.Message:
            ...


class ReplyEmbedGetter:
    def __init__(
        self, inter: ClutterInteraction, embed_creator: QuickEmbedCreator, /
    ) -> None:
        self.__inter = inter
        self.__embed_creator = embed_creator

    def __getattr__(self, item: str) -> ReplyEmbedCoroutine:
        async def runner(
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime.datetime | None = None,
            **kwargs: Any,
        ):
            return await self.__inter.responses.send_message(
                embed=self.__embed_creator(
                    item, title, description, url=url, timestamp=timestamp
                ),
                **kwargs,
            )

        return runner


class ClutterInteraction:
    client: Clutter

    def __init__(self, inter: discord.Interaction, /) -> None:
        self.__inter = inter

    def __getattr__(self, item: str, /) -> Any:
        return getattr(self.__inter, item)

    @property
    def reply_embed(self):
        return ReplyEmbedGetter(self, self.client.embed)
