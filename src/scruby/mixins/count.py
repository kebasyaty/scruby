# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for counting the number of documents."""

from __future__ import annotations

__all__ = ("Count",)

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from typing import Any, final


class Count:
    """Methods for counting the number of documents."""

    @final
    async def estimated_document_count(self) -> int:
        """Asynchronous method.

        Get an estimate of the number of documents in this collection using collection metadata.

        Returns:
            The number of documents.
        """
        meta = await self.get_meta()
        return meta.counter_documents

    @final
    async def count_documents(
        self,
        filter_fn: Callable,
    ) -> int:
        """Asynchronous method.

        Count the number of documents a matching the filter in this collection.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.

        Returns:
            The number of documents.
        """
        # Variable initialization
        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(self._max_number_branch)
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: Any = self._class_model
        stop_signal = Event()
        counter: int = 0
        # Run quantum loop
        with ThreadPoolExecutor(self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                docs = await future.result()
                if docs is not None:
                    counter += len(docs)
        return counter
