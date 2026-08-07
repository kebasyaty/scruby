# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for deleting documents."""

from __future__ import annotations

__all__ = ("Delete",)

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, final

import aiodbm
from anyio import Path


class Delete:
    """Methods for deleting documents."""

    @final
    @staticmethod
    async def _task_delete(
        filter_fn: Callable,
        branch_number: int,
        hash_reduce_left: int,
        db_root: str,
        class_model: Any,
        mode: int,
    ) -> int:
        """Asynchronous task for find and delete documents.

        This method is for internal use.

        Returns:
            The number of deleted documents.
        """
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        leaf_path = Path(
            *(
                db_root,
                class_model.__name__,
                separated_hash,
                "leaf.dbm",
            ),
        )
        counter: int = 0

        if await leaf_path.exists():
            async with aiodbm.open(str(leaf_path), flag="c", mode=mode) as leaf_db:
                keys = await leaf_db.keys()

                for key in keys:
                    doc_json = await leaf_db.get(key)
                    doc = class_model.model_validate_json(doc_json)
                    if filter_fn(doc):
                        await leaf_db.delete(key)
                        counter -= 1
        return counter

    @final
    async def delete_many(
        self,
        filter_fn: Callable,
    ) -> int:
        """Asynchronous method for delete one or more documents matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.

        Returns:
            The number of deleted documents.
        """
        # Variable initialization
        hash_reduce_left: int = self._hash_reduce_left
        assert hash_reduce_left != 0, "Scruby.run(hash_reduce_left = 0) - Not valid for `delete_many` method."

        search_task_fn: Callable = self._task_delete
        branch_numbers: range = range(self._max_number_branch)
        db_root: str = self._db_root
        class_model: Any = self._class_model
        mode = self._mode
        counter: int = 0

        # Run quantum loop
        with ThreadPoolExecutor(self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(
                    search_task_fn,
                    filter_fn,
                    branch_number,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    mode,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                counter += await future.result()
        if counter < 0:
            await self._counter_documents(counter)
        return abs(counter)
