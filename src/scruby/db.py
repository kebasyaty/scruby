"""Creation and management of the database.

Examples:
    >>> from scruby import Scruby
    >>> db = Scruby()
    >>> await db.set_key("key name", "Some text")
    None
    >>> await db.get_key("key name")
    "Some text"
    >>> await db.has_key("key name")
    True
    >>> await db.delete_key("key name")
    None
    >>> await db.napalm()
    None
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

    Examples:
        >>> from scruby import Scruby
        >>> db = Scruby()
        >>> await db.set_key("key name", "Some text")
        None
        >>> await db.get_key("key name")
        "Some text"
        >>> await db.has_key("key name")
        True
        >>> await db.delete_key("key name")
        None
        >>> await db.napalm()
        None

    Args:
        db_path: Path to root directory of databases. Defaule by = "ScrubyDB" (in root of project)
    """

    def __init__(  # noqa: D107
        self,
        db_path: str = "ScrubyDB",
    ) -> None:
        super().__init__()
        self.__db_path = db_path

    @property
    def db_path(self) -> str:
        """Get database name."""
        return self.__db_path

    async def get_leaf_path(self, key: str) -> Path:
        """Get the path to the database cell by key.

        Args:
            key: Key name.
        """
        # Key to md5 sum.
        key_md5: str = hashlib.md5(key.encode("utf-8")).hexdigest()  # noqa: S324
        # Convert md5 sum in the segment of path.
        segment_path_md5: str = "/".join(list(key_md5))
        # The path of the branch to the database.
        branch_path: Path = Path(
            *(self.__db_path, segment_path_md5),
        )
        # If the branch does not exist, need to create it.
        if not await branch_path.exists():
            await branch_path.mkdir(parents=True)
        # The path to the database cell.
        leaf_path: Path = Path(*(branch_path, "leaf.json"))
        return leaf_path

    async def set_key(
        self,
        key: str,
        value: ValueOfKey,
    ) -> None:
        """Asynchronous method for adding and updating keys to database.

        Examples:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set_key("key name", "Some text")
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

    async def get_key(self, key: str) -> ValueOfKey:
        """Asynchronous method for getting key from database.

        Examples:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set_key("key name", "Some text")
            None
            >>> await db.get_key("key name")
            "Some text"
            >>> await db.get_key("key missing")
            KeyError

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
        raise KeyError()

    async def has_key(self, key: str) -> bool:
        """Asynchronous method for checking presence of  key in database.

        Examples:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set_key("key name", "Some text")
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
            try:
                data[key]
                return True
            except KeyError:
                return False
        return False

    async def delete_key(self, key: str) -> None:
        """Asynchronous method for deleting key from database.

        Examples:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set_key("key name", "Some text")
            None
            >>> await db.delete_key("key name")
            None
            >>> await db.delete_key("key missing")
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
            del data[key]
            await leaf_path.write_bytes(orjson.dumps(data))
            return
        raise KeyError()

    async def napalm(self) -> None:
        """Asynchronous method for full database deletion (Arg: db_path).

        Warning:
            - `Be careful, this will remove all keys.`

        Examples:
            >>> from scruby import Scruby
            >>> db = Scruby()
            >>> await db.set_key("key name", "Some text")
            None
            >>> await db.napalm()
            None
            >>> await db.napalm()
            FileNotFoundError
        """
        await to_thread.run_sync(rmtree, self.__db_path)
        return
