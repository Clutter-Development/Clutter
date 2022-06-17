from __future__ import annotations

from typing import Callable

__all__ = ("esc", "make_color")


def esc(*codes: int) -> str:
    """Returns the ANSI escape sequence for the given codes.

    Args:
        *codes (int): The codes to make the ANSI escape sequence with.

    Returns:
        str: The ANSI escape sequence.
    """
    return f"\x1b[{';'.join(str(c) for c in codes)}m"


def make_color(start: str, end: str, /) -> Callable[[str], str]:
    """Returns a function that returns the given color.

    Args:
        start (str): The start code.
        end (str): The end code.

    Returns:
        Callable[[str], str]: The color function.
    """

    def color_func(s: str, /) -> str:
        return start + s + end

    return color_func
