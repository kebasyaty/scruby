"""Creation and management of the database."""

from __future__ import annotations

__all__ = ("Scruby",)

import concurrent.futures
import contextlib
import logging
import zlib
from collections.abc import Callable
from pathlib import Path as SyncPath
from shutil import rmtree
from typing import Any, Never, TypeVar, assert_never

import orjson
from anyio import Path, to_thread
from pydantic import BaseModel

from scruby import constants

logger = logging.getLogger(__name__)

T = TypeVar("T")


class _Meta(BaseModel):
    """Metadata of Collection."""

    counter_documents: int


class Scruby[T]:
    """Creation and management of database.

    Args:
        class_model: Class of Model (Pydantic).
    """

    def __init__(  # noqa: D107
        self,
        class_model: T,
    ) -> None:
        self.__meta = _Meta
        self.__class_model = class_model
        self.__db_root = constants.DB_ROOT
        self.__hash_reduce_left = constants.HASH_REDUCE_LEFT
        # The maximum number of keys.
        match self.__hash_reduce_left:
            case 0:
                self.__max_branch_number = 4294967296
            case 2:
                self.__max_branch_number = 16777216
            case 4:
                self.__max_branch_number = 65536
            case 6:
                self.__max_branch_number = 256
            case _ as unreachable:
                msg: str = f"{unreachable} - Unacceptable value for HASH_REDUCE_LEFT."
                logger.critical(msg)
                assert_never(Never(unreachable))
        # 1.Create metadata if absent.
        # 2.Check metadata.
        self._create_metadata()

    def _create_metadata(self) -> None:
        """Create metadata for collection if absent.

        This method is for internal use.
        """
        branch_number: int = 0
        key_as_hash: str = f"{branch_number:08x}"[self.__hash_reduce_left :]
        separated_hash: str = "/".join(list(key_as_hash))
        branch_path = SyncPath(
            *(
                self.__db_root,
                self.__class_model.__name__,
                separated_hash,
            ),
        )
        if not branch_path.exists():
            branch_path.mkdir(parents=True)
            meta = _Meta(
                counter_documents=0,
            )
            meta_json = meta.model_dump_json()
            meta_path = SyncPath(*(branch_path, "meta.json"))
            meta_path.write_text(meta_json, "utf-8")

    async def _get_meta_path(self) -> Path:
        """Asynchronous method for getting path to metadata of collection.

        This method is for internal use.
        """
        branch_number: int = 0
        branch_number_as_hash: str = f"{branch_number:08x}"[self.__hash_reduce_left :]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        return Path(
            *(
                self.__db_root,
                self.__class_model.__name__,
                separated_hash,
                "meta.json",
            ),
        )

    async def _get_meta(self) -> _Meta:
        """Asynchronous method for getting metadata of collection.

        This method is for internal use.
        """
        meta_path = await self._get_meta_path()
        meta_json = await meta_path.read_text()
        meta: _Meta = self.__meta.model_validate_json(meta_json)
        return meta

    async def _set_meta(self, meta: _Meta) -> None:
        """Asynchronous method for updating metadata of collection.

        This method is for internal use.
        """
        meta_path = await self._get_meta_path()
        meta_json = meta.model_dump_json()
        await meta_path.write_text(meta_json, "utf-8")

    async def _counter_documents(self, number: int) -> None:
        """Asynchronous method for management of documents in metadata of collection.

        This method is for internal use.
        """
        meta_path = await self._get_meta_path()
        meta_json = await meta_path.read_text("utf-8")
        meta: _Meta = self.__meta.model_validate_json(meta_json)
        meta.counter_documents += number
        if meta.counter_documents < 0:
            meta.counter_documents = 0
        meta_json = meta.model_dump_json()
        await meta_path.write_text(meta_json, "utf-8")

    def _sync_counter_documents(self, number: int) -> None:
        """Management of documents in metadata of collection.

        This method is for internal use.
        """
        branch_number: int = 0
        branch_number_as_hash: str = f"{branch_number:08x}"[self.__hash_reduce_left :]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        meta_path = SyncPath(
            *(
                self.__db_root,
                self.__class_model.__name__,
                separated_hash,
                "meta.json",
            ),
        )
        meta_json = meta_path.read_text("utf-8")
        meta: _Meta = self.__meta.model_validate_json(meta_json)
        meta.counter_documents += number
        if meta.counter_documents < 0:
            meta.counter_documents = 0
        meta_json = meta.model_dump_json()
        meta_path.write_text(meta_json, "utf-8")

    async def _get_leaf_path(self, key: str) -> Path:
        """Asynchronous method for getting path to collection cell by key.

        This method is for internal use.

        Args:
            key: Key name.
        """
        if not isinstance(key, str):
            logger.error("The key is not a type of `str`.")
            raise KeyError("The key is not a type of `str`.")
        if len(key) == 0:
            logger.error("The key should not be empty.")
            raise KeyError("The key should not be empty.")
        # Key to crc32 sum.
        key_as_hash: str = f"{zlib.crc32(key.encode('utf-8')):08x}"[self.__hash_reduce_left :]
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
        leaf_path: Path = await self._get_leaf_path(key)
        value_json: str = value.model_dump_json()
        # Write key-value to the database.
        if await leaf_path.exists():
            # Add new key or update existing.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            if data.get(key) is None:
                await self._counter_documents(1)
            data[key] = value_json
            await leaf_path.write_bytes(orjson.dumps(data))
        else:
            # Add new key to a blank leaf.
            await leaf_path.write_bytes(orjson.dumps({key: value_json}))
            await self._counter_documents(1)

    async def get_key(self, key: str) -> T:
        """Asynchronous method for getting value of key from collection.

        Args:
            key: Key name.
        """
        # The path to the database cell.
        leaf_path: Path = await self._get_leaf_path(key)
        # Get value of key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            obj: T = self.__class_model.model_validate_json(data[key])
            return obj
        msg: str = "`get_key` - The unacceptable key value."
        logger.error(msg)
        raise KeyError()

    async def has_key(self, key: str) -> bool:
        """Asynchronous method for checking presence of key in collection.

        Args:
            key: Key name.
        """
        # The path to the database cell.
        leaf_path: Path = await self._get_leaf_path(key)
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
        leaf_path: Path = await self._get_leaf_path(key)
        # Deleting key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            del data[key]
            await leaf_path.write_bytes(orjson.dumps(data))
            await self._counter_documents(-1)
            return
        msg: str = "`delete_key` - The unacceptable key value."
        logger.error(msg)
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
    def _task_find(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: str,
        db_root: str,
        class_model: T,
    ) -> dict[str, Any] | None:
        """Task for find documents.

        This method is for internal use.
        """
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        separated_hash: str = "/".join(list(branch_number_as_hash))
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
        """Finds a single document matching the filter.

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
        branch_numbers: range = range(1, self.__max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self.__hash_reduce_left
        db_root: str = self.__db_root
        class_model: T = self.__class_model
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for branch_number in branch_numbers:
                future = executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                )
                doc = future.result(timeout)
                if doc is not None:
                    return doc
        return None

    def find_many(
        self,
        filter_fn: Callable,
        db_query_docs_limit: int = 1000,
        max_workers: int | None = None,
        timeout: float | None = None,
    ) -> list[T] | None:
        """Finds one or more documents matching the filter.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            filter_fn: A function that execute the conditions of filtering.
            db_query_docs_limit: Limiting the number of request results. By default = 1000.
            max_workers: The maximum number of processes that can be used to
                         execute the given calls. If None or not given then as many
                         worker processes will be created as the machine has processors.
            timeout: The number of seconds to wait for the result if the future isn't done.
                     If None, then there is no limit on the wait time.
        """
        branch_numbers: range = range(1, self.__max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self.__hash_reduce_left
        db_root: str = self.__db_root
        class_model: T = self.__class_model
        counter: int = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            results = []
            for branch_number in branch_numbers:
                if counter == db_query_docs_limit:
                    break
                future = executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                )
                doc = future.result(timeout)
                if doc is not None:
                    results.append(doc)
                    counter += 1
        return results or None

    def collection_name(self) -> str:
        """Get collection name."""
        return self.__class_model.__name__

    def collection_full_name(self) -> str:
        """Get full name of collection."""
        return f"{self.__db_root}/{self.__class_model.__name__}"

    async def estimated_document_count(self) -> int:
        """Get an estimate of the number of documents in this collection using collection metadata."""
        meta = await self._get_meta()
        return meta.counter_documents

    def count_documents(
        self,
        filter_fn: Callable,
        max_workers: int | None = None,
        timeout: float | None = None,
    ) -> int:
        """Count the number of documents a matching the filter in this collection.

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
        branch_numbers: range = range(1, self.__max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self.__hash_reduce_left
        db_root: str = self.__db_root
        class_model: T = self.__class_model
        counter: int = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for branch_number in branch_numbers:
                future = executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                )
                if future.result(timeout) is not None:
                    counter += 1
        return counter

    @staticmethod
    def _task_delete(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: int,
        db_root: str,
        class_model: T,
    ) -> int:
        """Task for find and delete documents.

        This method is for internal use.
        """
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        leaf_path: SyncPath = SyncPath(
            *(
                db_root,
                class_model.__name__,
                separated_hash,
                "leaf.json",
            ),
        )
        counter: int = 0
        if leaf_path.exists():
            data_json: bytes = leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            new_data: dict[str, str] = {}
            for key, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    counter -= 1
                else:
                    new_data[key] = val
            leaf_path.write_bytes(orjson.dumps(new_data))
        return counter

    def find_many_and_delete(
        self,
        filter_fn: Callable,
        max_workers: int | None = None,
        timeout: float | None = None,
    ) -> int:
        """Finds one or more documents matching the filter and deletes their.

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
        branch_numbers: range = range(1, self.__max_branch_number)
        search_task_fn: Callable = self._task_delete
        hash_reduce_left: int = self.__hash_reduce_left
        db_root: str = self.__db_root
        class_model: T = self.__class_model
        counter: int = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for branch_number in branch_numbers:
                future = executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                )
                counter += future.result(timeout)
        if counter < 0:
            self._sync_counter_documents(counter)
        return abs(counter)

    @staticmethod
    def _task_get_docs(
        branch_number: int,
        hash_reduce_left: int,
        db_root: str,
        class_model: T,
    ) -> list[Any]:
        """Get documents for custom task.

        This method is for internal use.
        """
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        leaf_path: SyncPath = SyncPath(
            *(
                db_root,
                class_model.__name__,
                separated_hash,
                "leaf.json",
            ),
        )
        docs = []
        if leaf_path.exists():
            data_json: bytes = leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                docs.append(class_model.model_validate_json(val))
        return docs

    def run_custom_task(self, custom_task: Callable) -> Any:
        """Running custom task.

        This method running a task created on the basis of a quantum loop.
        Effectiveness running task depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.
        """
        kwargs = {
            "get_docs_fn": self._task_get_docs,
            "branch_numbers": range(1, self.__max_branch_number),
            "hash_reduce_left": self.__hash_reduce_left,
            "db_root": self.__db_root,
            "class_model": self.__class_model,
        }
        return custom_task(**kwargs)
