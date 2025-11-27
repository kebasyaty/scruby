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
from anyio import Path
from pydantic import BaseModel

from scruby import constants, mixins

logger = logging.getLogger(__name__)

T = TypeVar("T")


class _Meta(BaseModel):
    """Metadata of Collection."""

    db_root: str
    hash_reduce_left: int
    max_branch_number: int
    counter_documents: int


class Scruby[T](
    mixins.Keys,
    mixins.Find,
    mixins.CustomTask,
    mixins.Collection,
    mixins.Count,
    mixins.Delete,
):
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
                db_root=self.__db_root,
                hash_reduce_left=self.__hash_reduce_left,
                max_branch_number=self.__max_branch_number,
                counter_documents=0,
            )
            meta_json = meta.model_dump_json()
            meta_path = SyncPath(*(branch_path, "meta.json"))
            meta_path.write_text(meta_json, "utf-8")
        #
        mixins.Keys.__init__(self, class_model)
        mixins.Find.__init__(
            self,
            self.__db_root,
            self.__hash_reduce_left,
            self.__max_branch_number,
            class_model,
        )
        mixins.CustomTask.__init__(
            self,
            self.__db_root,
            self.__hash_reduce_left,
            self.__max_branch_number,
            class_model,
        )
        mixins.Collection.__init__(
            self,
            self.__db_root,
            class_model,
        )
        mixins.Count.__init__(
            self,
            self.__db_root,
            self.__hash_reduce_left,
            self.__max_branch_number,
            class_model,
        )
        mixins.Delete.__init__(
            self,
            self.__db_root,
            self.__hash_reduce_left,
            self.__max_branch_number,
            class_model,
        )

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

    @staticmethod
    def napalm() -> None:
        """Method for full database deletion.

        The main purpose is tests.

        Warning:
            - `Be careful, this will remove all keys.`

        Returns:
            None.
        """
        with contextlib.suppress(FileNotFoundError):
            rmtree(constants.DB_ROOT)
        return

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
