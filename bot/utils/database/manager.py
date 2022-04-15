from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Tuple, Union

from motor import motor_asyncio

from .misc import assemble_dict, find_in_dict, maybe_int

if TYPE_CHECKING:
    from pymongo.collection import Collection

__all__ = ("MongoManager",)


class MongoManager:
    def __init__(self, connect_url: str, port: int = None, /, *, database: str) -> None:  # type: ignore
        self._client = motor_asyncio.AsyncIOMotorClient(connect_url, port)
        self._db = self._client[database]

    def _parse_path(self, path: str, /) -> Tuple[List[str], Collection, Union[str, int]]:  # type: ignore
        """Parses the path.

        Args:
            path (str): The path to parse.

        Returns:
            0: The left path as a list. Might be empty.
            1: The MongoDB collection.
            2: The _id of the document. Can be a string or an integer.

        Raises:
            ValueError: If the path is too short
        """
        path = [_ for _ in path.split(".") if _ != ""]  # type: ignore
        if len(path) < 2:
            raise ValueError("Path must be at least 2 elements long: Collection and _id")
        collection = self._db[path.pop(0)]  # type: ignore
        _id = maybe_int(path.pop(0))  # type: ignore
        return path, collection, _id  # type: ignore

    async def get(self, path: str, /, *, default: Any = None) -> Any:
        """Fetches the variable from the database.

        Args:
            path (str): The path to the variable. Must be at least 2 elements long: Collection and _id.
            default (Any): The default value to return if the variable is not found.

        Returns:
            Any: The value of the variable.
        """
        path, collection, _id = self._parse_path(path)  # type: ignore
        if path:
            return find_in_dict(
                await collection.find_one({"_id": _id}, {"_id": 0, ".".join(path): 1}), path, default=default
                # type: ignore
            )
        return collection.find_one({"_id": _id}) or default

    async def set(self, path: str, value: Any, /) -> None:
        """Sets the variable in the database.

        Args:
            path (str): The path to the variable. Must be at least 2 elements long: Collection and _id.
            value (Any): The value to set the key to.
        """
        path, collection, _id = self._parse_path(path)  # type: ignore
        if not path and not isinstance(value, dict):
            raise ValueError("Value must be a dictionary if whole document is wanted to be updated.")
        if await collection.find_one({"_id": _id}, {"_id": 1}):
            val = {"$set": {".".join(path): value}} if path else value
            await collection.update_one({"_id": _id}, val)
        else:
            val = assemble_dict(path, value) if path else value  # type: ignore
            await collection.insert_one({"_id": _id, **val})

    async def push(self, path: str, value: Any, /, *, allow_dupes: bool = True) -> bool:
        """Appends the variable to a list in the database.

        Args:
            path (str): The path to the list. Must be at least 3 elements long: Collection and _id.
            value (Any): The value to append to the list.
            allow_dupes (bool): If true, the value will be appended to the list. If false, the value will be appended if it is not in the list.

        Returns:
            bool: If the value was pushed.

        Raises:
            ValueError: If the path is too short.
        """
        path, collection, _id = self._parse_path(path)  # type: ignore
        if not path:
            raise ValueError("Path must be at least 3 elements long: Collection, _id and key for the push operation.")
        if doc := await collection.find_one({"_id": _id}) is None:
            await collection.insert_one({"_id": _id, **assemble_dict(path, [value])})  # type: ignore
            return True
        elif allow_dupes or value not in find_in_dict(doc, path, default=[]):  # type: ignore
            await collection.update_one({"_id": _id}, {"$push": {".".join(path): value}})
            return True
        return False

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
        path, collection, _id = self._parse_path(path)  # type: ignore
        if not path:
            raise ValueError("Path must be at least 3 elements long: Collection, _id and key for the pull operation.")
        if value in find_in_dict(await collection.find_one({"_id": _id}, {".".join(path): 1}), path,
                                 default=[]):  # type: ignore
            await collection.update_one({"_id": _id}, {"$pull": {".".join(path): value}})
            return True
        return False

    async def rem(self, path: str, /) -> None:  # FIXME TODO: shit code
        """Removes the col/doc/var from the database.

        Args:
            path (str): The path to the col/doc/var. Must be at least 1 element long.

        Raises:
            ValueError: If the path is too short.
        """
        path = [_ for _ in path.split(".") if _ != ""]  # type: ignore
        if not path:
            raise ValueError("Path not given. Cannot delete entire database.")
        collection = self._db[path.pop(0)]  # type: ignore
        if not path:
            await collection.drop()
            return
        _id = maybe_int(path.pop(0))  # type: ignore
        if not path:
            await collection.delete_one({"_id": _id})
        else:
            await collection.update_one({"_id": _id}, {"$unset": {".".join(path): ""}})
