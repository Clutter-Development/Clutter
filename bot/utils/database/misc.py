from typing import Any, Dict, List, Optional, TypeVar, Union

__all__ = ("assemble_dict", "find_in_dict", "maybe_int")

T = TypeVar("T")
NestedDict = Dict[str, Union["NestedDict", Any]]


def assemble_dict(path: List[str], value: Any, /) -> NestedDict:
    """Assembles a nested dictionary from the path and value.

    Args:
        path (List[str]): The path to the value.
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


def find_in_dict(get_from: dict, path: List[str], /, *, default: Optional[Any] = None) -> Any:
    """Finds the key value pair in the specified dictionary.

    Args:
        get_from (dict): The dictionary to get the value from.
        path (List[str]): The path to the value.
        default (Any): The default value to return if the key is not found.

    Returns:
        Optional[Any]: The value. Returns the default value if the key is not found.
    """
    key = path.pop(-1)
    for _ in path:
        try:
            get_from = get_from[_]
        except (KeyError, TypeError, AttributeError):
            return None
    return get_from.get(key, default)


def maybe_int(value: T, /) -> Union[int, T]:
    """Converts the value to an int if possible.

    Args:
        value (T): The value to convert.

    Returns:
        Union[int, T]: The converted? value.
    """
    try:
        value = int(value)  # type: ignore
    finally:
        return value
