from typing import Any, TypeVar

__all__ = ("find_in_nested_dict", "NestedDict")

T = TypeVar("T")
NestedDict = dict[str, Any | "NestedDict"]


def find_in_nested_dict(
    find_in: NestedDict, path: str | list[str], /, *, default: T = None
) -> Any | T:
    """Finds the value that is in the path.

    Args:
        find_in (NestedDict): The dictionary to get the value from.
        path (str | list[str]): The path to the value.
        default (T, optional): The default value to return if the key is not found. Defaults to None.

    Returns:
        Any | T: The value. Returns the default value if the key is not found.
    """
    if isinstance(path, str):
        return find_in_nested_dict(find_in, path.split("."), default=default)

    for key in path:
        try:
            find_in = find_in[key]
        except (KeyError, TypeError):
            return default

    return find_in
