from typing import TYPE_CHECKING, Any, Protocol

from discord.ext import commands

if TYPE_CHECKING:
    import datetime

    import discord
    from core.bot import Clutter
    from discord_utils import QuickEmbedCreator

__all__ = ("ClutterContext",)


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
        self, context: commands.Context, embed_creator: QuickEmbedCreator, /
    ) -> None:
        self._context = context
        self._embed_creator = embed_creator

    def __getattr__(self, item: str) -> ReplyEmbedCoroutine:
        async def runner(
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime.datetime | None = None,
            **kwargs: Any,
        ):
            return await self._context.reply(
                embed=self._embed_creator.__call__(
                    item, title, description, url=url, timestamp=timestamp
                ),
                **kwargs,
            )

        return runner


class ClutterContext(commands.Context):
    bot: Clutter
    reply_embed: ReplyEmbedGetter

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.reply_embed = ReplyEmbedGetter(self, self.bot.embed)

    async def ok(self, value: bool, /) -> None:
        emojis = self.bot._config["STYLE"]["EMOJIS"]
        await self.message.add_reaction(emojis["SUCCESS" if value else "ERROR"])
