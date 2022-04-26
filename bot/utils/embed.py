from __future__ import annotations

from typing import TYPE_CHECKING, Callable, overload

from discord import Embed

if TYPE_CHECKING:
    from core.bot import Clutter

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, bot: Clutter, /) -> None:
        self._style = bot.config["STYLE"]

    def __getattr__(self, item: str, /) -> Callable[[str | None, str | None], Embed]:
        """Returns an embed with the given asset type.

        Args:
            item (str): The asset type to use.

        Returns:
            Callable[[str, str], Embed]: A function that returns an embed with the given asset type.
        """
        return self.__call__(item)

    @overload
    def __call__(self, item: str, /) -> Callable[[str | None, str | None], Embed]:
        ...

    @overload
    def __call__(self, item: str, title: str | None, /, description: str | None = None) -> Embed:  # sourcery skip: instance-method-first-arg-name
        ...

    def __call__(
        self, asset_type: str, title: str | None = None, /, description: str | None = None
    ) -> Callable[[str | None, str | None], Embed] | Embed:
        def embed(title_: str | None = None, description_: str | None = None) -> Embed:
            nonlocal asset_type
            asset_type = asset_type.upper()
            color = self._style["COLORS"][asset_type]
            emoji = self._style["EMOJIS"][asset_type]
            return Embed(title=f"{emoji} {title_}", description=description_, color=color)

        if title or description:
            return embed(title, description)
        else:
            return embed
