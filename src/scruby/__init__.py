"""A fast key-value storage library.

Scruby is a fast key-value storage library that provides an ordered mapping from string keys to string values.
The library uses fractal-tree addressing.

The maximum size of the database is 16**32=340282366920938463463374607431768211456 branches,
each branch can store one or more keys.

The value of any key can be obtained in 32 steps, thereby achieving high performance.
There is no need to iterate through all the keys in search of the desired value.
"""

from __future__ import annotations

__all__ = ("Scruby",)

import hashlib
from typing import Literal

import orjson
from anyio import Path

type ValueOfKey = str | int | float | list | dict | Literal[True] | Literal[False] | None


class Scruby:
    """Creation and management of the database.

    Example:
        >>> from scruby import Scruby
        >>> db = Scruby()
        >>> await db.set("key name", "Some text")
        None
        >>> await db.get("key name")
        "Some text"
        >>> await db.has("key name")
        True
        >>> await db.delete("key name")
        None
        >>> await db.clear()
        None
        >>> await db.napalm()
        None

    Args:
        root_store: Root directory for databases. Defaule by = "ScrubyDB"
        db_name: Database name. Defaule by = "store"
    """

    def __init__(  # noqa: D107
        self,
        root_store: str = "ScrubyDB",
        db_name: str = "store",
    ) -> None:
        super().__init__()
        self.__root_store = root_store
        self.__db_name = db_name

    @property
    def root_store(self) -> str:
        """Get name of root directory of database."""
        return self.__root_store

    @property
    def db_name(self) -> str:
        """Add or update key-value pair(s) to the database."""
        return self.__db_name

    async def set(
        self,
        key: str,
        value: ValueOfKey,
    ) -> None:
        """Asynchronous method for adding and updating values of keys to database.

        Example:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set("key name", "Some text")
            None

        Args:
            key: Key name.
            value: Value of key.
        """
        # Key to md5 sum.
        key_md5: str = hashlib.md5(key.encode("utf-8")).hexdigest()  # noqa: S324
        # Convert md5 sum in the segment of path.
        path_md5: str = key_md5.split().join("/")
        # The path of the branch to the database cell.
        branch_path: Path = Path(*(self.root_store, self.db_name, path_md5))
        # If the branch does not exist, need to create it.
        if not await branch_path.exists():
            await branch_path.mkdir(parents=True)
        # The path to the database cell.
        leaf_path: Path = Path(*(branch_path, "leaf.json"))
        # Write key-value to the database.
        if await leaf_path.exists():
            # Add new key or update existing.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            data[key] = value
            await leaf_path.write_bytes(orjson.dumps(data))
        else:
            # Add new key to a blank leaf.
            await leaf_path.write_bytes(data=orjson.dumps({key: value}))
