"""Creation and management of the database."""

from __future__ import annotations

__all__ = ("Scruby",)

import concurrent.futures
import contextlib
import zlib
from collections.abc import Callable
from pathlib import Path as SyncPath
from shutil import rmtree
from typing import Any, Never, TypeVar, assert_never

import orjson
from anyio import Path, to_thread

from scruby import constants

T = TypeVar("T")


class Scruby[T]:
    """Creation and management of database.

    Args:
        class_model: Class of Model (Pydantic).
    """

    def __init__(  # noqa: D107
        self,
        class_model: T,
    ) -> None:
        self.__class_model = class_model
        self.__db_root = constants.DB_ROOT
        self.__length_reduction_hash = constants.LENGTH_REDUCTION_HASH
        # The maximum number of keys.
        match self.__length_reduction_hash:
            case 0:
                self.__max_num_keys = 4294967296
            case 2:
                self.__max_num_keys = 16777216
            case 4:
                self.__max_num_keys = 65536
            case 6:
                self.__max_num_keys = 256
            case _ as unreachable:
                assert_never(Never(unreachable))

    async def get_leaf_path(self, key: str) -> Path:
        """Asynchronous method for getting path to collection cell by key.

        Args:
            key: Key name.
        """
        if not isinstance(key, str):
            raise KeyError("The key is not a type of `str`.")
        if len(key) == 0:
            raise KeyError("The key should not be empty.")
        # Key to crc32 sum.
        key_as_hash: str = f"{zlib.crc32(key.encode('utf-8')):08x}"[self.__length_reduction_hash :]
        # Convert crc32 sum in the segment of path.
        separated_hash: str = "/".join(list(key_as_hash))
        # The path of the branch to the database.
        branch_path: Path = Path(
            *(
                self.__db_root,
                self.__class_model.__name__,
                separated_hash,
            ),
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
        value: T,
    ) -> None:
        """Asynchronous method for adding and updating keys to collection.

        Args:
            key: Key name.
            value: Value of key.
        """
        # The path to the database cell.
        leaf_path: Path = await self.get_leaf_path(key)
        value_json: str = value.model_dump_json()
        # Write key-value to the database.
        if await leaf_path.exists():
            # Add new key or update existing.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            data[key] = value_json
            await leaf_path.write_bytes(orjson.dumps(data))
        else:
            # Add new key to a blank leaf.
            await leaf_path.write_bytes(orjson.dumps({key: value_json}))

    async def get_key(self, key: str) -> T:
        """Asynchronous method for getting value of key from collection.

        Args:
            key: Key name.
        """
        # The path to the database cell.
        leaf_path: Path = await self.get_leaf_path(key)
        # Get value of key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            obj: T = self.__class_model.model_validate_json(data[key])
            return obj
        raise KeyError()

    async def has_key(self, key: str) -> bool:
        """Asynchronous method for checking presence of key in collection.

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
        """Asynchronous method for deleting key from collection.

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

    @staticmethod
    async def napalm() -> None:
        """Asynchronous method for full database deletion.

        The main purpose is tests.

        Warning:
            - `Be careful, this will remove all keys.`
        """
        with contextlib.suppress(FileNotFoundError):
            await to_thread.run_sync(rmtree, constants.DB_ROOT)
        return

    @staticmethod
    def search_task(
        key: int,
        filter_fn: Callable,
        length_reduction_hash: str,
        db_root: str,
        class_model: T,
    ) -> dict[str, Any] | None:
        """Search task."""
        key_as_hash: str = f"{key:08x}"[length_reduction_hash:]
        separated_hash: str = "/".join(list(key_as_hash))
        leaf_path: SyncPath = SyncPath(
            *(
                db_root,
                class_model.__name__,
                separated_hash,
                "leaf.json",
            ),
        )
        if leaf_path.exists():
            data_json: bytes = leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    return doc
        return None

    def find_one(
        self,
        filter_fn: Callable,
        max_workers: int | None = None,
        timeout: float | None = None,
    ) -> T | None:
        """Find a single document.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            filter_fn: A function that execute the conditions of filtering.
            max_workers: The maximum number of processes that can be used to
                         execute the given calls. If None or not given then as many
                         worker processes will be created as the machine has processors.
            timeout: The number of seconds to wait for the result if the future isn't done.
                     If None, then there is no limit on the wait time.
        """
        keys: range = range(1, self.__max_num_keys)
        search_task_fn: Callable = self.search_task
        length_reduction_hash: int = self.__length_reduction_hash
        db_root: str = self.__db_root
        class_model: T = self.__class_model
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for key in keys:
                future = executor.submit(
                    search_task_fn,
                    key,
                    filter_fn,
                    length_reduction_hash,
                    db_root,
                    class_model,
                )
                result = future.result(timeout)
                if result is not None:
                    return result
        return None
