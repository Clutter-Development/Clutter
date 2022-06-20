from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Literal, overload

from motor.motor_asyncio import AsyncIOMotorClient

from .misc import create_nested_dict, find_in_nested_dict, maybe_int

if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from motor.motor_asyncio import (
        AsyncIOMotorCollection,
        AsyncIOMotorDatabase,
    )

__all__ = ("MongoManager",)


class MongoManager:
    def __init__(
        self, connect_url: str, port: int | None = None, *, database: str
    ) -> None:
        self._client = AsyncIOMotorClient(connect_url, port)
        self._db: AsyncIOMotorDatabase = self._client[database]

    def _parse_path(self, path: str) -> tuple[AsyncIOMotorCollection, str | int, str]:  # type: ignore

        path: list[str] = path.split(".", 2)

        if len(path) < 2:
            raise ValueError(
                "Path must be at least 2 elements long: Collection and _id."
            )

        collection = self._db[path.pop(0)]
        _id = maybe_int(path.pop(0))

        return collection, _id, next(iter(path), "")

    @overload
    async def ping(self, *, return_is_alive: Literal[False] = False) -> float:
        ...

    @overload
    async def ping(
        self, *, return_is_alive: Literal[True] = ...
    ) -> tuple[float, bool]:
        ...

    async def ping(
        self, *, return_is_alive: bool = False
    ) -> float | tuple[float, bool]:
        ts = time.time()
        response = await self._db.command("ping")
        ts = time.time() - ts

        if return_is_alive:
            return ts, bool(response or {}.get("ok", False))

        return ts

    async def get(self, path: str, *, default: Any = None) -> Any:
        collection, _id, path = self._parse_path(path)

        return find_in_nested_dict(
            await collection.find_one(
                {"_id": _id}, {"_id": 0, path: 1} if path else None
            ),
            path,
            default=default,
        )

    async def set(self, path: str, value: Any) -> None:

        collection, _id, path = self._parse_path(path)

        if not path and not isinstance(value, dict):
            raise ValueError(
                "The value must be a dictionary if whole document is wanted to"
                " be updated."
            )

        if await collection.find_one({"_id": _id}, {"_id": 1}):
            await collection.update_one(
                {"_id": _id}, {"$set": {path: value} if path else value}
            )

        else:
            await collection.insert_one(
                {"_id": _id, **create_nested_dict(path, value)}
            )

    async def push(
        self, path: str, value: Any, *, allow_duplicates: bool = True
    ) -> bool:
        collection, _id, path = self._parse_path(path)

        if not path:
            raise ValueError(
                "Path must be at least 3 elements long: Collection, _id and"
                " key for the push operation."
            )

        if not (doc := await collection.find_one({"_id": _id}, {"_id": 1})):
            await collection.insert_one(
                {"_id": _id, **create_nested_dict(path, [value])}  # type: ignore
            )
            return True

        if allow_duplicates or value not in find_in_nested_dict(
            doc, path, default=[]
        ):
            await collection.update_one({"_id": _id}, {"$push": {path: value}})
            return True

        return False

    async def pull(self, path: str, value: Any) -> bool:
        collection, _id, path = self._parse_path(path)

        if not path:
            raise ValueError(
                "Path must be at least 3 elements long: Collection, _id and"
                " key for the pull operation."
            )

        if value in find_in_nested_dict(
            await collection.find_one({"_id": _id}, {path: 1}),
            path,
            default=[],
        ):
            await collection.update_one({"_id": _id}, {"$pull": {path: value}})
            return True

        return False

    async def rem(self, path: str) -> None:  # type: ignore

        path: list[str] = path.split(".", 2)

        if not path:
            raise ValueError("Path not given. Cannot delete entire database.")

        collection = self._db[path.pop(0)]

        if not path:
            await collection.drop()
            return

        _id = maybe_int(path.pop(0))

        if not path:
            await collection.delete_one({"_id": _id})
        else:
            await collection.update_one(
                {"_id": _id}, {"$unset": {path[0]: ""}}
            )
