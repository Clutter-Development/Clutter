from __future__ import annotations

from typing import Callable, Dict

from discord import Embed

__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, colors: Dict[str, int], emojis: Dict[str, str],  /) -> None:
        self._color = colors
        self._emojis = emojis

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
            color = self._color[asset_type.upper()]
            emoji = self._emojis[asset_type.upper()]
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
