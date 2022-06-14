from typing import Any

from lru import LRU

from .manager import MongoManager

__all__ = ("CachedMongoManager",)


class CachedMongoManager(MongoManager):
    def __init__(
        self,
        connect_url: str,
        port: int | None = None,
        /,
        *,
        database: str,
        max_items: int,
    ) -> None:
        """Initialize the CachedMongoManager class.

        Args:
            connect_url (str): The MongoDB URI to use to connect to the database.
            port (int | None, optional): The port of the MongoDB instance, used when the db is hosted locally. Defaults to None.
            database (str): The database to use.
            max_items (int): The max items the cache can hold.
        """
        self._cache = LRU(max_items)
        super().__init__(connect_url, port, database=database)

    def uncache(self, key: str | list[str], /, *, match: bool = True) -> None:
        """Uncaches the key value pair with the given path. If match is False, it will uncache all key value pairs that start with the path.

        Args:
            key (str | list[str]): The key(s) to uncache.
            match (bool, optional): If not to delete all keys starting with the path.
        """
        if isinstance(key, list):
            for single_key in key:
                self.uncache(single_key, match=match)

        elif match:
            del self._cache[key]

        else:
            for ikey in self._cache.keys():
                if ikey.startswith(key):
                    del self._cache[ikey]

    async def get(self, path: str, /, *, default: Any = None) -> Any:
        if path in self._cache:
            return self._cache[path]

        value = await super().get(path, default=default)

        self._cache[path] = value

        return value

    async def set(self, path: str, value: Any, /) -> None:
        await super().set(path, value)
        self.uncache(path)

    async def push(
        self, path: str, value: Any, /, *, allow_duplicates: bool = True
    ) -> bool:
        res = await super().push(path, value, allow_duplicates=allow_duplicates)
        self.uncache(path)
        return res

    async def pull(self, path: str, value: Any, /) -> bool:
        res = await super().pull(path, value)
        self.uncache(path)
        return res

    async def rem(self, path: str, /) -> None:
        await super().rem(path)
        self.uncache(path)
