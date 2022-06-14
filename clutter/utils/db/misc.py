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
    """Assembles a nested dictionary from the path and value. ("abc.def.ghi", 123) => {"abc": {"def": {"ghi": 123}}}

    Args:
        path (str | list[str]): The path to the value in keys, seperated by a dot (.).
        value (Any): The value to set.

    Returns:
        NestedDict: The nested dictionary.
    """
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
    """Finds the value that is in the path.

    Args:
        find_in (NestedDict | None): The dictionary to get the value from.
        path (str | list[str]): The path to the value.
        default (Any, optional): The default value to return if the key is not found. Defaults to None.

    Returns:
        Any: The value. Returns the default value if the key is not found.
    """
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
    """Converts the value to an int if possible.

    Args:
        value (T): The value to convert.

    Returns:
        int | T: The converted value. returns the original value if it couldn't be converter to an integer.
    """
    try:
        value = int(value)  # type: ignore
    finally:
        return value
