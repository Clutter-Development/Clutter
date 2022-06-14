from typing import TYPE_CHECKING, Any

import discord

if TYPE_CHECKING:
    import datetime

    from typing_extensions import Self

__all__ = ("Embed",)


class Embed(discord.Embed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        *,
        url: str | None = None,
        timestamp: datetime.datetime | None = None,
        color: int | discord.Color | None = None,
    ):
        super().__init__(
            title=title,
            description=description,
            url=url,
            timestamp=timestamp,
            color=color,
        )

    def add_field(
        self, title: Any, description: Any, *, inline: bool = False
    ) -> Self:
        return super().add_field(name=title, value=description, inline=inline)
