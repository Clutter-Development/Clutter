from io import StringIO

import discord

__all__ = ("text_file",)


def text_file(text: str, file_name: str, /, *, spoiler: bool = False) -> discord.File:
    return discord.File(StringIO(text), file_name, spoiler=spoiler)  # type: ignore
