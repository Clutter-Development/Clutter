from typing import TYPE_CHECKING, Any

from discord import Color, Embed

if TYPE_CHECKING:
    from datetime import datetime

    # noinspection PyUnresolvedReferences
    from typing_extensions import Self

__all__ = ("Embed",)


class Embed(Embed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        *,
        url: str | None = None,
        timestamp: datetime | None = None,
        color: int | Color | None = None,
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
