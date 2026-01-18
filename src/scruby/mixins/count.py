# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for counting the number of documents."""

from __future__ import annotations

__all__ = ("Count",)

import concurrent.futures
from collections.abc import Callable
from typing import Any


class Count:
    """Methods for counting the number of documents."""

    async def estimated_document_count(self) -> int:
        """Asynchronous method.

        Get an estimate of the number of documents in this collection using collection metadata.

        Returns:
            The number of documents.
        """
        meta = await self.get_meta()
        return meta.counter_documents

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
        counter: int = 0
        # Run quantum loop
        with concurrent.futures.ThreadPoolExecutor(self._max_workers) as executor:
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
                    counter += len(docs)
        return counter
