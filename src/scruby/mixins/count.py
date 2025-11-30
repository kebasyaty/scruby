"""Methods for counting the number of documents."""

from __future__ import annotations

__all__ = ("Count",)

import concurrent.futures
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class Count[T]:
    """Methods for counting the number of documents."""

    async def estimated_document_count(self) -> int:
        """Get an estimate of the number of documents in this collection using collection metadata.

        Returns:
            The number of documents.
        """
        meta = await self.get_meta()
        return meta.counter_documents

    async def count_documents(
        self,
        filter_fn: Callable,
        max_workers: int | None = None,
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

        Returns:
            The number of documents.
        """
        branch_numbers: range = range(1, self._max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: T = self._class_model
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
                if await future.result() is not None:
                    counter += 1
        return counter
