from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from discord import Embed

if TYPE_CHECKING:
    from ..main import Clutter

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, bot: Clutter, /) -> None:
        self._style = bot.config["STYLE"]

        # Predefined embeds
        self.success = self._assemble_embed("success")
        self.error = self._assemble_embed("error")
        self.warning = self._assemble_embed("warning")
        self.info = self._assemble_embed("info")

    def _assemble_embed(self, asset_type: str, /) -> Callable[[str, str], Embed]:
        """Makes a function that returns an embed with the given asset type.

        Args:
            asset_type (str): The asset type to use.

        Returns:
            Callable[[str, str], Embed]: A function that returns an embed with the given asset type.
        """

        def create_embed(title: str, description: Optional[str] = None, /) -> Embed:
            """Creates an embed with the colors and emojis from the server configuration.

            Args:
                title (str): The title of the embed.
                description (str): The description of the embed.

            Returns:
                Embed: The embed.
            """
            color = self._style["COLORS"][asset_type.upper()]
            emoji = self._style["EMOJIS"][asset_type.upper()]
            return Embed(title=f"{emoji} {title}", description=description, color=color)

        return create_embed

    def __call__(self, asset_type: str, title: str, description: Optional[str] = None, /) -> Embed:
        """Creates an embed with the colors and emojis from the configuration.

        Args:
            asset_type (str): The asset type to use.
            title (str): The title of the embed.
            description (str): The description of the embed.

        Returns:
            Embed: The embed.
        """
        return self._assemble_embed(asset_type)(title, description)  # type: ignore
