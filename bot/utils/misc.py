import io
import re

import discord

__all__ = ("text_file", "listify")


def text_file(text: str, file_name: str, /, *, spoiler: bool = False) -> discord.File:
    """Creates a discord.File object from a string.

    Args:
        text (str): The text to be converted to a discord.File object.
        file_name (str): The name of the file.
        spoiler (bool, optional): Whether or not the file is a spoiler. Defaults to False.

    Returns:
        discord.File: The discord.File object.
    """
    return discord.File(io.BytesIO(bytes(text, "utf-8")), file_name, spoiler=spoiler)


def listify(title: str, description: str, /) -> str:
    """Makes a fancy list(ish) thing out of a title and description

    Args:
        title (str): The title of the list.
        description (str): The description of the list.

    Returns:
        str: The listified string

    Example:
        Title Here:
           ╭──────╯
           │Description
           │Stuff
           │etc
    """
    newline = "\n"
    non_ansi = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", title)
    return f"{title}:\n   ╭{(len(non_ansi.split(newline)[-1]) - 4) * '─'}╯\n{'   │' + f'{newline}   │'.join(description.split(newline))}"
