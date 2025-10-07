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
from typing import Any, Literal, Never, TypeVar, assert_never

import orjson
from anyio import Path, to_thread
from pydantic import BaseModel

from scruby import constants
from scruby.errors import (
    KeyAlreadyExistsError,
    KeyNotExistsError,
)

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
        # The maximum number of branches.
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
        # Caching a pati for metadata in the form of a tuple.
        # The zero branch is reserved for metadata.
        branch_number: int = 0
        branch_number_as_hash: str = f"{branch_number:08x}"[constants.HASH_REDUCE_LEFT :]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        self.__meta_path_tuple = (
            constants.DB_ROOT,
            class_model.__name__,
            separated_hash,
            "meta.json",
        )
        # Create metadata for collection, if required.
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

    async def _get_meta(self) -> _Meta:
        """Asynchronous method for getting metadata of collection.

        This method is for internal use.

        Returns:
            Metadata object.
        """
        meta_path = Path(*self.__meta_path_tuple)
        meta_json = await meta_path.read_text()
        meta: _Meta = self.__meta.model_validate_json(meta_json)
        return meta

    async def _set_meta(self, meta: _Meta) -> None:
        """Asynchronous method for updating metadata of collection.

        This method is for internal use.

        Returns:
            None.
        """
        meta_json = meta.model_dump_json()
        meta_path = Path(*self.__meta_path_tuple)
        await meta_path.write_text(meta_json, "utf-8")

    async def _counter_documents(self, step: Literal[1, -1]) -> None:
        """Asynchronous method for management of documents in metadata of collection.

        This method is for internal use.

        Returns:
            None.
        """
        meta_path = Path(*self.__meta_path_tuple)
        meta_json = await meta_path.read_text("utf-8")
        meta: _Meta = self.__meta.model_validate_json(meta_json)
        meta.counter_documents += step
        meta_json = meta.model_dump_json()
        await meta_path.write_text(meta_json, "utf-8")

    def _sync_counter_documents(self, number: int) -> None:
        """Management of documents in metadata of collection.

        This method is for internal use.
        """
        meta_path = SyncPath(*self.__meta_path_tuple)
        meta_json = meta_path.read_text("utf-8")
        meta: _Meta = self.__meta.model_validate_json(meta_json)
        meta.counter_documents += number
        meta_json = meta.model_dump_json()
        meta_path.write_text(meta_json, "utf-8")

    async def _get_leaf_path(self, key: str) -> Path:
        """Asynchronous method for getting path to collection cell by key.

        This method is for internal use.

        Args:
            key: Key name.

        Returns:
            Path to cell of collection.
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

    async def add_key(
        self,
        key: str,
        value: T,
    ) -> None:
        """Asynchronous method for adding key to collection.

        Args:
            key: Key name. Type `str`.
            value: Value of key. Type `BaseModel`.

        Returns:
            None.
        """
        # The path to cell of collection.
        leaf_path: Path = await self._get_leaf_path(key)
        value_json: str = value.model_dump_json()
        # Write key-value to collection.
        if await leaf_path.exists():
            # Add new key.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            try:
                data[key]
            except KeyError:
                data[key] = value_json
                await leaf_path.write_bytes(orjson.dumps(data))
            else:
                err = KeyAlreadyExistsError()
                logger.error(err.message)
                raise err
        else:
            # Add new key to a blank leaf.
            await leaf_path.write_bytes(orjson.dumps({key: value_json}))
        await self._counter_documents(1)

    async def update_key(
        self,
        key: str,
        value: T,
    ) -> None:
        """Asynchronous method for updating key to collection.

        Args:
            key: Key name. Type `str`.
            value: Value of key. Type `BaseModel`.

        Returns:
            None.
        """
        # The path to cell of collection.
        leaf_path: Path = await self._get_leaf_path(key)
        value_json: str = value.model_dump_json()
        # Update the existing key.
        if await leaf_path.exists():
            # Update the existing key.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            try:
                data[key]
                data[key] = value_json
                await leaf_path.write_bytes(orjson.dumps(data))
            except KeyError:
                err = KeyNotExistsError()
                logger.error(err.message)
                raise err from None
        else:
            logger.error("The key not exists.")
            raise KeyError()

    async def get_key(self, key: str) -> T:
        """Asynchronous method for getting value of key from collection.

        Args:
            key: Key name.

        Returns:
            Value of key or KeyError.
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

        Returns:
            True, if the key is present.
        """
        # Get path to cell of collection.
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

        Returns:
            None.
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

        Returns:
            None.
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
    ) -> list[T] | None:
        """Task for find documents.

        This method is for internal use.

        Returns:
            List of documents or None.
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
        docs: list[T] = []
        if leaf_path.exists():
            data_json: bytes = leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    docs.append(doc)
        return docs or None

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

        Returns:
            Document or None.
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
                docs = future.result(timeout)
                if docs is not None:
                    return docs[0]
        return None

    def find_many(
        self,
        filter_fn: Callable,
        limit_docs: int = 1000,
        max_workers: int | None = None,
        timeout: float | None = None,
    ) -> list[T] | None:
        """Finds one or more documents matching the filter.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            filter_fn: A function that execute the conditions of filtering.
            limit_docs: Limiting the number of documents. By default = 1000.
            max_workers: The maximum number of processes that can be used to
                         execute the given calls. If None or not given then as many
                         worker processes will be created as the machine has processors.
            timeout: The number of seconds to wait for the result if the future isn't done.
                     If None, then there is no limit on the wait time.

        Returns:
            List of documents or None.
        """
        branch_numbers: range = range(1, self.__max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self.__hash_reduce_left
        db_root: str = self.__db_root
        class_model: T = self.__class_model
        counter: int = 0
        result: list[T] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for branch_number in branch_numbers:
                if counter >= limit_docs:
                    return result[:limit_docs]
                future = executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                )
                docs = future.result(timeout)
                if docs is not None:
                    for doc in docs:
                        if counter >= limit_docs:
                            return result[:limit_docs]
                        result.append(doc)
                        counter += 1
        return result or None

    def collection_name(self) -> str:
        """Get collection name.

        Returns:
            Collection name.
        """
        return self.__class_model.__name__

    def collection_full_name(self) -> str:
        """Get full name of collection.

        Returns:
            Full name of collection.
        """
        return f"{self.__db_root}/{self.__class_model.__name__}"

    async def estimated_document_count(self) -> int:
        """Get an estimate of the number of documents in this collection using collection metadata.

        Returns:
            The number of documents.
        """
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

        Returns:
            The number of documents.
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

        Returns:
            The number of deleted documents.
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
            new_state: dict[str, str] = {}
            for key, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    counter -= 1
                else:
                    new_state[key] = val
            leaf_path.write_bytes(orjson.dumps(new_state))
        return counter

    def delete_many(
        self,
        filter_fn: Callable,
        max_workers: int | None = None,
        timeout: float | None = None,
    ) -> int:
        """Delete one or more documents matching the filter.

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

        Returns:
            The number of deleted documents.
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

        Returns:
            List of documents.
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
        docs: list[str, T] = []
        if leaf_path.exists():
            data_json: bytes = leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                docs.append(class_model.model_validate_json(val))
        return docs

    def run_custom_task(self, custom_task_fn: Callable, limit_docs: int = 1000) -> Any:
        """Running custom task.

        This method running a task created on the basis of a quantum loop.
        Effectiveness running task depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            custom_task_fn: A function that execute the custom task.
            limit_docs: Limiting the number of documents. By default = 1000.

        Returns:
            The result of a custom task.
        """
        kwargs = {
            "get_docs_fn": self._task_get_docs,
            "branch_numbers": range(1, self.__max_branch_number),
            "hash_reduce_left": self.__hash_reduce_left,
            "db_root": self.__db_root,
            "class_model": self.__class_model,
            "limit_docs": limit_docs,
        }
        return custom_task_fn(**kwargs)

    @staticmethod
    def _task_update(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: str,
        db_root: str,
        class_model: T,
        new_data: dict[str, Any],
    ) -> int:
        """Task for find documents.

        This method is for internal use.

        Returns:
            The number of updated documents.
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
            new_state: dict[str, str] = {}
            for _, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    for key, value in new_data.items():
                        doc.__dict__[key] = value
                        new_state[key] = doc.model_dump_json()
                    counter += 1
            leaf_path.write_bytes(orjson.dumps(new_state))
        return counter

    def update_many(
        self,
        filter_fn: Callable,
        new_data: dict[str, Any],
        max_workers: int | None = None,
        timeout: float | None = None,
    ) -> int:
        """Updates one or more documents matching the filter.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            filter_fn: A function that execute the conditions of filtering.
            new_data: New data for the fields that need to be updated.
            max_workers: The maximum number of processes that can be used to
                         execute the given calls. If None or not given then as many
                         worker processes will be created as the machine has processors.
            timeout: The number of seconds to wait for the result if the future isn't done.
                     If None, then there is no limit on the wait time.

        Returns:
            The number of updated documents.
        """
        branch_numbers: range = range(1, self.__max_branch_number)
        update_task_fn: Callable = self._task_update
        hash_reduce_left: int = self.__hash_reduce_left
        db_root: str = self.__db_root
        class_model: T = self.__class_model
        counter: int = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for branch_number in branch_numbers:
                future = executor.submit(
                    update_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    new_data,
                )
                counter += future.result(timeout)
        return counter
