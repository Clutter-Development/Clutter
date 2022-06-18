from __future__ import annotations

from asyncio import to_thread
from typing import Awaitable, Callable, ParamSpec, TypeVar

__all__ = ("run_in_executor",)

T = TypeVar("T")
P = ParamSpec("P")


def run_in_executor(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await to_thread(func, *args, **kwargs)

    return wrapper
