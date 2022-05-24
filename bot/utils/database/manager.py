from __future__ import annotations

from typing import TYPE_CHECKING, Any

from motor.motor_asyncio import AsyncIOMotorClient

from .misc import assemble_dict, find_in_dict, maybe_int

if TYPE_CHECKING:
    from pymongo.collection import Collection

__all__ = ("MongoManager",)


class MongoManager:
    def __init__(self, connect_url: str, port: int | None = None, /, *, database: str) -> None:
        """Initialize the MongoManager class.

        Args:
            connect_url (str): The MongoDB URI to use to connect to the database
            database (str): The database to use.
            port (int | None, optional): The port of the MongoDB instance, used when the db is hosted locally. Defaults to None.
        """
        self._client = AsyncIOMotorClient(connect_url, port)
        self._db = self._client[database]

    def _parse_path(self, path: str, /) -> tuple[list[str], Collection, str | int]:
        """Parses a path string and returns the excess, a mongo collection and a str or int.

        Args:
            path (str): The path to parse

        Raises:
            ValueError: If the path is too short

        Returns:
            tuple[list[str], Collection, str | int]: The excess path as a list, the MongoDB collection, the _id of the document. can be a str or an int
        """
        ppath = [_ for _ in path.split(".") if _ != ""]
        if len(ppath) < 2:
            raise ValueError("Path must be at least 2 elements long: Collection and _id")
        collection = self._db[ppath.pop(0)]
        _id = maybe_int(ppath.pop(0))
        return ppath, collection, _id

    async def get(self, path: str, /, *, default: Any = None) -> Any:
        """Fetches the variable from the database.

        Args:
            path (str): The path to the variable. Must be at least 2 elements long: Collection and _id.
            default (Any, optional): The default value to return if the variable is not found.

        Returns:
            Any: The value of the variable.
        """
        ppath, collection, _id = self._parse_path(path)
        if ppath:
            return find_in_dict(
                await collection.find_one({"_id": _id}, {"_id": 0, ".".join(ppath): 1}) or {},
                ppath,
                default=default,
            )
        return collection.find_one({"_id": _id}) or default

    async def set(self, path: str, value: Any, /) -> None:
        """Sets the variable in the database.

        Args:
            path (str): The path to the variable. Must be at least 2 elements long: Collection and _id.
            value (Any): The value to set the key to.
        """
        ppath, collection, _id = self._parse_path(path)
        if not ppath and not isinstance(value, dict):
            raise ValueError(
                "Value must be a dictionary if whole document is wanted to be updated."
            )
        if await collection.find_one({"_id": _id}, {"_id": 1}):
            val = {"$set": {".".join(ppath): value}} if ppath else value
            await collection.update_one({"_id": _id}, val)
        else:
            val = assemble_dict(ppath, value) if ppath else value
            await collection.insert_one({"_id": _id, **val})

    async def push(self, path: str, value: Any, /, *, allow_dupes: bool = True) -> bool:
        """Appends the variable to a list in the database.

        Args:
            path (str): The path to the list. Must be at least 3 elements long: Collection and _id.
            value (Any): The value to append to the list.
            allow_dupes (bool, optional): If true, the value will be appended to the list. If false, the value will be appended if it is not in the list.

        Raises:
            ValueError: If the path is too short.

        Returns:
            bool: If the value was pushed.
        """
        ppath, collection, _id = self._parse_path(path)
        if not ppath:
            raise ValueError(
                "Path must be at least 3 elements long: Collection, _id and key for the push operation."
            )
        if (doc := await collection.find_one({"_id": _id})) is None:
            await collection.insert_one({"_id": _id, **assemble_dict(ppath, [value])})
            return True
        if allow_dupes or value not in find_in_dict(doc, ppath, default=[]):
            await collection.update_one({"_id": _id}, {"$push": {".".join(ppath): value}})
            return True
        return False

    async def pull(self, path: str, value: Any, /) -> bool:
        """Removes the variable from a list in the database.

        Args:
            path (str): The path to the list. Must be at least 3 elements long: Collection and _id.
            value (Any): The value to remove from the list.

        Raises:
            ValueError: If the path is too short.

        Returns:
            bool: If the value was removed.
        """
        ppath, collection, _id = self._parse_path(path)
        if not ppath:
            raise ValueError(
                "Path must be at least 3 elements long: Collection, _id and key for the pull operation."
            )
        if value in find_in_dict(
            await collection.find_one({"_id": _id}, {".".join(ppath): 1}), ppath, default=[]
        ):
            await collection.update_one({"_id": _id}, {"$pull": {".".join(ppath): value}})
            return True
        return False

    async def rem(self, path: str, /) -> None:
        """Removes the col/doc/var from the database.

        Args:
            path (str): The path to the col/doc/var. Must be at least 1 element long.

        Raises:
            ValueError: If the path is too short.
        """
        ppath = [_ for _ in path.split(".") if _ != ""]
        if not ppath:
            raise ValueError("Path not given. Cannot delete entire database.")
        collection = self._db[ppath.pop(0)]
        if not ppath:
            await collection.drop()
            return
        _id = maybe_int(ppath.pop(0))
        if not ppath:
            await collection.delete_one({"_id": _id})
        else:
            await collection.update_one({"_id": _id}, {"$unset": {".".join(ppath): ""}})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()
