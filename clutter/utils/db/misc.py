from __future__ import annotations

from typing import Any, SupportsInt, TypeVar, overload

__all__ = (
    "create_nested_dict",
    "find_in_nested_dict",
    "maybe_int",
    "NestedDict",
)

T = TypeVar("T")
NestedDict = dict[str, Any | "NestedDict"]


def create_nested_dict(path: str | list[str], value: T, /) -> NestedDict | T:
    if not path:
        return value

    if isinstance(path, str):
        return create_nested_dict(path.split("."), value)

    assembled = {}
    reference = assembled

    for key in path[:-1]:
        assembled[key] = {}
        assembled = assembled[key]

    assembled[path[-1]] = value

    return reference


def find_in_nested_dict(
    find_in: NestedDict | None, path: str | list[str], /, *, default: T = None
) -> Any | T:
    if isinstance(path, str):
        return find_in_nested_dict(find_in, path.split("."), default=default)

    for key in path:
        try:
            find_in = find_in[key]  # type: ignore
        except (KeyError, TypeError):
            return default

    return find_in


@overload
def maybe_int(value: SupportsInt, /) -> int:
    ...


@overload
def maybe_int(value: T, /) -> T:
    ...


def maybe_int(value: SupportsInt | T, /) -> int | T:
    try:
        value = int(value)  # type: ignore
    finally:
        return value
