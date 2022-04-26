from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Any  # , overload

from discord import Embed

if TYPE_CHECKING:
    from core.bot import Clutter

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, bot: Clutter, /) -> None:
        """Initialize the EmbedBuilder class.

        Args:
            bot (Clutter): The bot to use to get the needed info from.
        """
        self._style = bot.config["STYLE"]

    def __getattr__(self, item: str, /):  # -> Callable[[str | None, str | None], Embed]:
        """Returns a function that returns an embed with the given asset type

        Args:
            item (str): The asset type to use.

        Returns:
            Callable[[str | None, str | None], Embed]: A function that returns an embed with the given asset type.
        """
        return self.__call__(item)

    # @overload
    # def __call__(self, item: str, /) -> Callable[[str | None, str | None], Embed]:
    #     ...

    # @overload
    # def __call__(self, item: str, title: str | None, /, description: str | None = None) -> Embed:  # sourcery skip: instance-method-first-arg-name
    #     ...

    def __call__(
            self, asset_type: str, title: str | None = None, /, description: str | None = None
    ):  # -> Callable[[str | None, str | None], Embed] | Embed:
        """Returns either an embed or a function that returns an embed

        Args:
            asset_type (str): The asset type to use.
            title (str | None, optional): The title of the embed, if this arg and the param arg is not given, a function will be returned. Defaults to None.
            description (str | None, optional): The description of the embed. Defaults to None.

        Returns:
            Callable[[str | None, str | None], Embed] | Embed: The result embed/function.
        """

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
