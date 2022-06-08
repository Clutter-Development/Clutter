from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from discord.ext import commands

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
        self, ctx: ClutterContext, embed_creator: QuickEmbedCreator, /
    ) -> None:
        self.__ctx = ctx
        self.__embed_creator = embed_creator

    def __getattr__(self, item: str) -> ReplyEmbedCoroutine:
        async def runner(
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime.datetime | None = None,
            **kwargs: Any,
        ) -> discord.Message:
            return await self.__ctx.reply(
                embed=self.__embed_creator.__call__(
                    item, title, description, url=url, timestamp=timestamp
                ),
                **kwargs,
            )

        return runner


class ClutterContext(commands.Context):
    bot: Clutter

    @property
    def reply_embed(self) -> ReplyEmbedGetter:
        return ReplyEmbedGetter(self, self.bot.embed)

    async def i18n(self, text: str, /, *, use_guild: bool = False) -> str:
        return await self.bot.i18n(self, text, use_guild=use_guild)

    async def ok(self, value: bool, /) -> None:
        emojis = self.bot.config["STYLE"]["EMOJIS"]
        await self.message.add_reaction(emojis["SUCCESS" if value else "ERROR"])
