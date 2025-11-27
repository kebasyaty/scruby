"""Methods for deleting documents."""

from __future__ import annotations

import concurrent.futures
import logging
from collections.abc import Callable
from pathlib import Path as SyncPath
from typing import TypeVar

import orjson

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Delete[T]:
    """Methods for deleting documents."""

    def __init__(  # noqa: D107
        self,
        db_root: str,
        hash_reduce_left: int,
        max_branch_number: int,
        class_model: T,
    ) -> None:
        self.__db_root = db_root
        self.__hash_reduce_left = hash_reduce_left
        self.__max_branch_number = max_branch_number
        self.__class_model = class_model

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
