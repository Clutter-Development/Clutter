from __future__ import annotations

from typing import Callable

__all__ = ("esc", "make_color")


def esc(*codes: int) -> str:
    return f"\x1b[{';'.join(str(c) for c in codes)}m"


def make_color(start: str, end: str) -> Callable[[str], str]:
    def color_func(s: str) -> str:
        return start + s + end

    return color_func
