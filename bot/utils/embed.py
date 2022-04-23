from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Union, overload

from discord import Embed

if TYPE_CHECKING:
    from ..main import Clutter

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, bot: Clutter, /) -> None:
        self._style = bot.config["STYLE"]

    def __getattr__(self, item: str, /) -> Callable[[str, Optional[str]], Embed]:
        """Returns an embed with the given asset type.

        Args:
            item (str): The asset type to use.

        Returns:
            Callable[[str, str], Embed]: A function that returns an embed with the given asset type.
        """
        return self.__call__(item)

    @overload
    def __call__(self, item: str, /) -> Callable[[Optional[str], Optional[str]], Embed]:
        ...

    @overload
    def __call__(self, item: str, title: str, /) -> Embed:
        ...

    @overload
    def __call__(self, item: str, title: str, description: str, /) -> Embed:
        ...

    def __call__(
            self,
            asset_type: str,
            title: Optional[str] = None,
            description: Optional[str] = None,
            /
    ) -> Union[Callable[[Optional[str], Optional[str]], Embed], Embed]:
        def embed(title_: Optional[str] = None, description_: Optional[str] = None) -> Embed:
            color = self._style["COLORS"][asset_type.upper()]
            emoji = self._style["EMOJIS"][asset_type.upper()]
            return Embed(title=f"{emoji} {title_}", description=description_, color=color)

        if title or description:
            return embed(title, description)
        else:
            return embed
