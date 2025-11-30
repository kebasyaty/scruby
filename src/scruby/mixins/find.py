"""Quantum methods for searching documents."""

from __future__ import annotations

__all__ = ("Find",)

import concurrent.futures
import logging
from collections.abc import Callable
from typing import TypeVar

import orjson
from anyio import Path

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Find[T]:
    """Quantum methods for searching documents."""

    @staticmethod
    async def _task_find(
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
        leaf_path: Path = Path(
            *(
                db_root,
                class_model.__name__,
                separated_hash,
                "leaf.json",
            ),
        )
        docs: list[T] = []
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    docs.append(doc)
        return docs or None

    async def find_one(
        self,
        filter_fn: Callable,
        max_workers: int | None = None,
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

        Returns:
            Document or None.
        """
        branch_numbers: range = range(1, self._max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: T = self._class_model
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
                docs = await future.result()
                if docs is not None:
                    return docs[0]
        return None

    async def find_many(
        self,
        filter_fn: Callable,
        limit_docs: int = 1000,
        max_workers: int | None = None,
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

        Returns:
            List of documents or None.
        """
        branch_numbers: range = range(1, self._max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: T = self._class_model
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
                docs = await future.result()
                if docs is not None:
                    for doc in docs:
                        if counter >= limit_docs:
                            return result[:limit_docs]
                        result.append(doc)
                        counter += 1
        return result or None
