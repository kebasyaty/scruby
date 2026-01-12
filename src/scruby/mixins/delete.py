# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for deleting documents."""

from __future__ import annotations

__all__ = ("Delete",)

import concurrent.futures
from collections.abc import Callable
from typing import Any

import orjson
from anyio import Path


class Delete:
    """Methods for deleting documents."""

    @staticmethod
    async def _task_delete(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: int,
        db_root: str,
        class_model: Any,
    ) -> int:
        """Task for find and delete documents.

        This method is for internal use.

        Returns:
            The number of deleted documents.
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
        counter: int = 0
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            new_state: dict[str, str] = {}
            for key, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    counter -= 1
                else:
                    new_state[key] = val
            await leaf_path.write_bytes(orjson.dumps(new_state))
        return counter

    async def delete_many(
        self,
        filter_fn: Callable,
    ) -> int:
        """Delete one or more documents matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.

        Returns:
            The number of deleted documents.
        """
        # Variable initialization
        search_task_fn: Callable = self._task_delete
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
                counter += await future.result()
        if counter < 0:
            await self._counter_documents(counter)
        return abs(counter)
