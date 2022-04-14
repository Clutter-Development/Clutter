from typing import Any, List, TypeVar, Union

__all__ = ["assemble_dict", "find_in_dict", "maybe_int"]


def assemble_dict(path: List[str], value: Any, /) -> dict:
    """Assembles a nested dictionary from the path and value."""
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


def find_in_dict(get_from: dict, path: List[str], /, *, default: Any = None) -> Any:
    """Finds the key value pair in the specified dictionary."""
    key = path.pop(-1)
    for _ in path:
        try:
            get_from = get_from[_]
        except (KeyError, TypeError, AttributeError):
            return None
    return get_from.get(key, default)


T = TypeVar("T")


def maybe_int(value: T, /) -> Union[int, T]:
    """Converts the value to an int if possible."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return value
