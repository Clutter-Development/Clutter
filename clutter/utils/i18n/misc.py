from __future__ import annotations

from typing import Any, TypeVar

__all__ = ("find_in_nested_dict", "NestedDict")

T = TypeVar("T")
NestedDict = dict[str, Any | "NestedDict"]


def find_in_nested_dict(
    find_in: NestedDict, path: str | list[str], /, *, default: T = None
) -> Any | T:
    if isinstance(path, str):
        return find_in_nested_dict(find_in, path.split("."), default=default)

    for key in path:
        try:
            find_in = find_in[key]
        except (KeyError, TypeError):
            return default

    return find_in
