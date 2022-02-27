import asyncio
import copy
import math
import time
from typing import Any, Union

from pymongo import MongoClient


class MongoManager:
    def __init__(self, connect_url: str, database: str, *, cooldown: int) -> None:
        self._client = MongoClient(connect_url)
        self._db = self._client[database]
        self._cache = {}
        self._cooldown = cooldown

    @staticmethod
    def _assemble_dict(path: list, value: Any) -> dict:
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

    @staticmethod
    def _find_in_dict(get_from: dict, path: list) -> Any:
        """Finds the key value pair in the specified dictionary."""
        key = path.pop(-1)
        for _ in path:
            try:
                get_from = get_from[_]
            except (KeyError, TypeError, AttributeError):
                return None
        return get_from.get(key, None)

    def _parse_path(self, path: str) -> Any:
        """Parses the path."""
        path = [_ for _ in path.split(".") if _ != ""]
        while len(path) < 3:
            path.append("_")
        collection = self._db[path.pop(0)]
        _id = path.pop(0)
        return path, collection, _id

    def _get_last_used(self, path: str) -> int:
        """Returns the time in seconds since the last used time of the variable."""
        return math.floor(time.time()) - self._cache[path][1] if path in self._cache.keys() else 0

    def _use(self, path: str) -> None:
        """Sets the last used time for the variable to now."""
        self._cache[path] = [self._cache[path][0], math.floor(time.time())]

    def _remove_after_cooldown(self, path: str) -> None:
        """Removes the variable from the cache if it hasn't been used for the cooldown after the cooldown time has passed."""
        time.sleep(self._cooldown + 0.1)
        if self._get_last_used(path) > self._cooldown:
            self._cache.pop(path)

    def _get_from_db(self, path: str) -> Any:
        """Fetches the variable from the database."""
        path, collection, _id = self._parse_path(path)
        result = collection.find_one({"_id": _id}, {"_id": 0, ".".join(path): 1})
        if not result:
            return None
        return self._find_in_dict(result, path)

    def refresh(self, path: Union[str, list]) -> None:
        """Refreshes the variable from the database."""
        if isinstance(path, str):
            for key in copy.copy(self._cache).keys():
                if key.startswith(path):  # The reason for this is that im treating the path like a dictionary.
                    self._cache.pop(key)
            return
        for _ in path:
            self.refresh(_)

    def set(self, path: str, value: Any) -> None:
        """Sets the variable in the database."""
        path_raw = copy.copy(path)
        path, collection, _id = self._parse_path(path)
        if collection.find_one({"_id": _id}, {"_id": 1}) is None:
            collection.insert_one({"_id": _id, **self._assemble_dict(path, value)})
        else:
            collection.update_one({"_id": _id}, {"$set": {".".join(path): value}})
        self.refresh(path_raw)

    def push(self, path: str, value: Any) -> None:
        """Appends the variable to a list in the database."""
        path_raw = copy.copy(path)
        path, collection, _id = self._parse_path(path)
        if collection.find_one({"_id": _id}, {"_id": 1}) is None:
            collection.insert_one({"_id": _id, **self._assemble_dict(path, [value])})
        else:
            collection.update_one({"_id": _id}, {"$push": {".".join(path): value}})
        self.refresh(path_raw)

    def pull(self, path: str, value: Any) -> None:
        """Removes the variable from a list in the database."""
        path_raw = copy.copy(path)
        path, collection, _id = self._parse_path(path)
        if collection.find_one({"_id": _id}, {"_id": 1}) is not None:
            collection.update_one({"_id": _id}, {"$pull": {".".join(path): value}})
            self.refresh(path_raw)

    def get(self, path: str, default: Any = None) -> Any:
        """Returns the variable from the cache if it's not too old, otherwise fetches it from the database."""
        if path in self._cache.keys():
            self._use(path)
        else:
            self._cache[path] = [self._get_from_db(path), math.floor(time.time())]
        asyncio.get_event_loop().run_in_executor(None, self._remove_after_cooldown, path)
        if self._cache.get(path, [None])[0] is None:
            return default
        return self._cache[path][0]

    def rem(self, path: str) -> None:
        """Removes the variable from the database."""
        path_raw = copy.copy(path)
        path = [_ for _ in path.split(".") if _ != ""]
        collection = self._db[path.pop(0)]
        if not path:
            collection.drop()
            return
        _id = path.pop(0)
        if not path:
            collection.delete_one({"_id": _id})
            return
        collection.update_one({"_id": _id}, {"$unset": {".".join(path): ""}})
        self.refresh(path_raw)
        return
