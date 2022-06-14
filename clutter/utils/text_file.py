import io

import discord

__all__ = ("TextFile",)


class TextFile(discord.File):
    def __init__(
        self,
        text: str,
        /,
        filename: str | None = None,
        *,
        spoiler: bool = discord.utils.MISSING,
        description: str | None = None,
        encoding: str = "utf-8",
    ):
        super().__init__(
            io.BytesIO(bytes(text, encoding)),
            filename,
            spoiler=spoiler,
            description=description,
        )
