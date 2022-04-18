from __future__ import annotations

from typing import Callable, Dict, Union

from discord import Embed

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, style: Dict[str, Dict[str, Union[str, int]]], /) -> None:
        self._style = style

        # Predefined embeds
        self.success = self._assemble_embed("success")
        self.error = self._assemble_embed("error")
        self.warning = self._assemble_embed("warning")
        self.info = self._assemble_embed("info")

    def _assemble_embed(self, asset_type: str, /) -> Callable:
        """Makes a function that returns an embed with the given asset type.

        Args:
            asset_type (str): The asset type to use.
        """

        def create_embed(title: str, description: str, /) -> Embed:
            """Creates an embed with the colors and emojis from the server configuration.

            Args:
                title (str): The title of the embed.
                description (str): The description of the embed.
            """
            color = self._style["COLORS"][asset_type.upper()]
            emoji = self._style["EMOJIS"][asset_type.upper()]
            return Embed(title=f"{emoji} {title}", description=description, color=color)

        return create_embed

    def __call__(self, asset_type: str, title: str, description: str, /) -> Embed:
        """Creates an embed with the colors and emojis from the configuration.

        Args:
            asset_type (str): The asset type to use.
            title (str): The title of the embed.
            description (str): The description of the embed.
        """
        return self._assemble_embed(asset_type)(title, description)
