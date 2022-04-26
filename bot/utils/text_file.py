from io import BytesIO

import discord

__all__ = ("text_file",)


def text_file(text: str, file_name: str, /, *, spoiler: bool = False) -> discord.File:
    """Creates a discord.File object from a string.

    Args:
        text (str): The text to be converted to a discord.File object.
        file_name (str): The name of the file.
        spoiler (bool, optional): Whether or not the file is a spoiler. Defaults to False.

    Returns:
        discord.File: The discord.File object.
    """
    return discord.File(BytesIO(bytes(text, "utf-8")), file_name, spoiler=spoiler)
