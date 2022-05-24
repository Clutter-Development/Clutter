from typing import Any, TypeVar

__all__ = ("assemble_dict", "find_in_dict", "maybe_int", "NestedDict")

T = TypeVar("T")
NestedDict = dict[str, Any | "NestedDict"]


def assemble_dict(path: list[str], value: Any, /) -> NestedDict:
    """Assembles a nested dictionary from the path and value.

    Args:
        path (list[str]): The path to the value.
        value (Any): The value to set.

    Returns:
        NestedDict: The assembled dictionary.
    """
    to_asm, i = {}, 0
    ref = to_asm
    if not path:
        return value
    for _ in path:
        i += 1
        if i == len(path):
            to_asm[_] = value
            break
        to_asm[_] = {}
        to_asm = to_asm[_]
    return ref


def find_in_dict(get_from: dict, path: list[str], /, *, default: Any = None) -> Any:
    """Finds the key value pair in the specified dictionary.

    Args:
        get_from (dict): The dictionary to get the value from.
        path (list[str]): The path to the value.
        default (Any, optional): The default value to return if the key is not found. Defaults to None.

    Returns:
        Any: The value. Returns the default value if the key is not found.
    """
    # print(f"Finding in dict:\n{get_from}\nPath: {'.'.join(path)}\nDefault: {default}")
    key = path.pop(-1)
    for _ in path:
        try:
            get_from = get_from[_]
        except (KeyError, TypeError, AttributeError):
            return default
    return get_from.get(key, default)


def maybe_int(value: T, /) -> int | T:
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
