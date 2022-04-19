import asyncio
import math
import time
from typing import Any, List, Union, Optional, Dict, Any

from .manager import MongoManager

__all__ = ("CachedMongoManager",)


class CachedMongoManager(MongoManager):
    def __init__(self, connect_url: str, port: Optional[int] = None, /, *, database: str, cooldown: float) -> None:
        self._cache: Dict[str, Any] = {}
        self._start_time: int = math.floor(time.time())
        self.cooldown: float = cooldown
        super().__init__(connect_url, port, database=database)

    def _current_time(self) -> int:
        """Returns the current time in seconds.

        Returns:
            int: The current time in seconds.
        """
        return math.floor(time.time()) - self._start_time

    def _get_last_used(self, path: str, /) -> int:
        """Returns the time in seconds since the last used time of the variable.

        Args:
            path (str): The variable to get the last used time of.

        Returns:
            int: The time in seconds since the last used time of the variable.
        """
        return (self._current_time() - self._cache[path][1]) if path in self._cache.keys() else 0

    def _use(self, path: str, /) -> None:
        """Sets the last used time for the variable to now.

        Args:
            path (str): The variable to set the last used time to now.
        """
        self._cache[path][1] = self._current_time()

    async def _remove_after_cooldown(self, path: str, /) -> None:
        """Removes the variable from the cache if it hasn't been used for the cooldown after the cooldown time has passed.

        Args:
            path (str): The variable to remove if it hasn't been used for the cooldown after the cooldown time has passed.
        """
        await asyncio.sleep(self.cooldown)
        if self._get_last_used(path) >= self.cooldown:
            self._cache.pop(path, None)

    def refresh(self, path: Union[str, List[str]], /, *, match: Optional[bool] = False) -> None:
        """Uncaches all variables that start with the given path. If match is True, only uncaches the given path.

        Args:
            path (Union[str, List[str]]): The variable(s) to uncache.
            match (Optional[bool]): Whether to match the path exactly or to start with it.
        """
        if isinstance(path, str):
            if match:
                self._cache.pop(path)
                return
            for key in self._cache.copy().keys():
                if key.startswith(path):
                    self._cache.pop(key)
            return
        for _ in path:
            self.refresh(_)

    async def get(self, path: str, /, *, default: Optional[Any] = None) -> Any:
        """Fetches the variable from the database.

        Args:
            path (str): The path to the variable. Must be at least 2 elements long: Collection and _id.
            default (Any): The default value to return if the variable is not found.

        Returns:
            Optional[Any]: The value of the variable.
        """
        if path in self._cache:
            self._use(path)
        else:
            self._cache[path] = [await super().get(path), self._current_time()]
        asyncio.create_task(self._remove_after_cooldown(path))
        if self._cache.get(path, [None])[0] is None:
            return default
        return self._cache[path][0]

    async def set(self, path: str, value: Any, /) -> None:
        """Sets the variable in the database.

        Args:
            path (str): The path to the variable. Must be at least 2 elements long: Collection and _id.
            value (Any): The value to set the key to.
        """
        await super().set(path, value)
        self.refresh(path)

    async def push(self, path: str, value: Any, /, *, allow_dupes: Optional[bool] = True) -> bool:
        """Appends the variable to a list in the database.

        Args:
            path (str): The path to the list. Must be at least 3 elements long: Collection and _id.
            value (Any): The value to append to the list.
            allow_dupes (Optional[bool]): If true, the value will be appended to the list. If false, the value will be appended if it is not in the list.

        Returns:
            bool: If the value was pushed.

        Raises:
            ValueError: If the path is too short.
        """
        val = await super().push(path, value, allow_dupes=allow_dupes)
        self.refresh(path)
        return val

    async def pull(self, path: str, value: Any, /) -> bool:
        """Removes the variable from a list in the database.

        Args:
            path (str): The path to the list. Must be at least 3 elements long: Collection and _id.
            value (Any): The value to remove from the list.

        Returns:
            bool: If the value was removed.

        Raises:
            ValueError: If the path is too short.
        """
        val = await super().pull(path, value)
        self.refresh(path)
        return val

    async def rem(self, path: str, /) -> None:
        """Removes the col/doc/var from the database.

        Args:
            path (str): The path to the col/doc/var. Must be at least 1 element long.

        Raises:
            ValueError: If the path is too short.
        """
        await super().rem(path)
        self.refresh(path)
