import io

from discord import File
from discord.utils import MISSING

__all__ = ("TextFile",)


class TextFile(File):
    def __init__(
        self,
        text: str,
        /,
        filename: str | None = None,
        *,
        spoiler: bool = MISSING,
        description: str | None = None,
        encoding: str = "utf-8",
    ):
        super().__init__(
            io.BytesIO(bytes(text, encoding)),
            filename,
            spoiler=spoiler,
            description=description,
        )
