from __future__ import annotations

from asyncio import to_thread
from typing import Awaitable, Callable, ParamSpec, TypeVar

__all__ = ("run_in_executor",)

T = TypeVar("T")
P = ParamSpec("P")


def run_in_executor(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """Makes a sync function non-blocking. This is meant to be used as a decorator.

    Args:
        func (Callable): The function to make 'async'.

    Returns:
        Callable[P, Awaitable]: The 'async' function.

    Example:
        @run_in_executor
        def blocking_func():
            ...

        async def main():
            await blocking_func()  # non-blocking now!

        asyncio.run(main())
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await to_thread(func, *args, **kwargs)

    return wrapper
