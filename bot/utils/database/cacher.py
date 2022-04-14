import asyncio
import copy
from math import floor
from time import time
from typing import Any, List, Union

from .manager import MongoManager

__all__ = ("CachedMongoManager",)


class CachedMongoManager:
    def __init__(self, connect_url: str, /, *, database: str, cooldown: int) -> None:
        self._manager = MongoManager(connect_url, database=database)
        self._cache = {}
        self._start_time = floor(time())
        self.cooldown = cooldown

    def _current_time(self) -> int:
        """Returns the current time in seconds."""
        return floor(time()) - self._start_time

    def _get_last_used(self, path: str) -> int:
        """Returns the time in seconds since the last used time of the variable."""
        return (self._current_time() - self._cache[path][1]) if path in self._cache.keys() else 0

    def _use(self, path: str) -> None:
        """Sets the last used time for the variable to now."""
        self._cache[path][1] = self._current_time()

    async def _remove_after_cooldown(self, path: str) -> None:
        """Removes the variable from the cache if it hasn't been used for the cooldown after the cooldown time has passed."""
        await asyncio.sleep(self.cooldown)
        if self._get_last_used(path) >= self.cooldown:
            # print(f"{path} hasn't been used for {self._get_last_used(path)} seconds, removing from cache.")
            self._cache.pop(path, None)

    def refresh(self, path: Union[str, List[str]], /, *, match: bool = False) -> None:
        """Uncaches all variables that start with the given path. If match is True, only uncaches the given path.

        Args:
            path (Union[str, List[str]]): The variable(s) to uncache.
            match (bool): Whether to match the path exactly or to start with it.
        """
        if isinstance(path, str):
            if match:
                self._cache.pop(path)
                return
            for key in copy.copy(self._cache).keys():
                if key.startswith(path):
                    self._cache.pop(key)
            return
        for _ in path:
            self.refresh(_)

    async def get(self, path: str, /, *, default: Any = None) -> Any:
        if path in self._cache:
            # print("Cache used: {}".format(path))
            self._use(path)
        else:
            # print("DB used: {}".format(path))
            self._cache[path] = [await self._manager.get(path), self._current_time()]
        asyncio.create_task(self._remove_after_cooldown(path))
        if self._cache.get(path, [None])[0] is None:
            return default
        return self._cache[path][0]

    async def set(self, path: str, value: Any, /) -> None:
        await self._manager.set(path, value)
        self.refresh(path, match=True)

    async def push(self, path: str, value: Any, /, *, allow_dupes: bool = True) -> bool:
        val = await self._manager.push(path, value, allow_dupes=allow_dupes)
        self.refresh(path, match=True)
        return val

    async def pull(self, path: str, value: Any, /) -> bool:
        val = await self._manager.pull(path, value)
        self.refresh(path, match=True)
        return val

    async def rem(self, path: str, /) -> None:
        val = await self._manager.rem(path)
        self.refresh(path, match=True)
        return val
