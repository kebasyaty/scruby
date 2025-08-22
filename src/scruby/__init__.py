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
from shutil import rmtree
from typing import Literal

import orjson
from anyio import Path, to_thread

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
        >>> await db.clean_store()
        None
        >>> await db.napalm()
        None

    Args:
        db_path: Path to root directory of databases. Defaule by = "ScrubyDB"
        store_name: Storage name for keys. Defaule by = "store_one"
    """

    def __init__(  # noqa: D107
        self,
        db_path: str = "ScrubyDB",
        store_name: str = "store_one",
    ) -> None:
        super().__init__()
        self.__db_path = db_path
        self.__store_name = store_name

    @property
    def db_path(self) -> str:
        """Get database name."""
        return self.__db_path

    @property
    def store_name(self) -> str:
        """Get store name."""
        return self.__store_name

    async def get_leaf_path(self, key: str) -> Path:
        """Get the path to the database cell by key.

        Args:
            key: Key name.
        """
        # Key to md5 sum.
        key_md5: str = hashlib.md5(key.encode("utf-8")).hexdigest()  # noqa: S324
        # Convert md5 sum in the segment of path.
        segment_path_md5: str = "/".join(key_md5.split())
        # The path of the branch to the database.
        branch_path: Path = Path(
            *(self.__db_path, self.__store_name, segment_path_md5),
        )
        # If the branch does not exist, need to create it.
        if not await branch_path.exists():
            await branch_path.mkdir(parents=True)
        # The path to the database cell.
        leaf_path: Path = Path(*(branch_path, "leaf.txt"))
        return leaf_path

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
        # The path to the database cell.
        leaf_path: Path = await self.get_leaf_path(key)
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

    async def get(self, key: str) -> ValueOfKey:
        """Get the value by key from the database.

        Example:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set("key name", "Some text")
            None
            >>> await db.get("key name")
            "Some text"
            >>> await db.get("key missing")
            None

        Args:
            key: Key name.
        """
        # The path to the database cell.
        leaf_path: Path = await self.get_leaf_path(key)
        # Get value of key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            return data[key]
        return None

    async def has(self, key: str) -> bool:
        """Check the presence of a key in the database.

        Example:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set("key name", "Some text")
            None
            >>> await db.has_key("key name")
            True
            >>> await db.has_key("key missing")
            False

        Args:
            key: Key name.
        """
        # The path to the database cell.
        leaf_path: Path = await self.get_leaf_path(key)
        # Checking whether there is a key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            return data.get(key) is not None
        return False

    async def delete(self, key: str) -> None:
        """Delete the key from the database.

        Example:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set("key name", "Some text")
            None
            >>> await db.delete("key name")
            None
            >>> await db.delete("key missing")
            KeyError

        Args:
            key: Key name.
        """
        # The path to the database cell.
        leaf_path: Path = await self.get_leaf_path(key)
        # Deleting key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            if data.get(key) is None:
                raise KeyError()
            del data[key]
            await leaf_path.write_bytes(orjson.dumps(data))
            return
        raise KeyError()

    async def clean_store(self) -> None:
        """Remove current storage (Arg: store_name).

        Warning:
            - `Be careful, this will remove all keys.`

        Example:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set("key name", "Some text")
            None
            >>> await db.clear()
            None
            >>> await db.clear()
            KeyError
        """
        store_path = f"{self.__db_path}/{self.__store_name}"
        await to_thread.run_sync(rmtree, store_path)
        return

    async def napalm(self) -> None:
        """Complete database deletion (Arg: db_path).

        Warning:
            - `Be careful, this will remove all stores with keys.`

        Example:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set("key name", "Some text")
            None
            >>> await db.napalm()
            None
            >>> await db.napalm()
            KeyError
        """
        await to_thread.run_sync(rmtree, self.__db_path)
        return
