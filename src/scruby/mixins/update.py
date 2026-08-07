# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for updating documents."""

from __future__ import annotations

__all__ = ("Update",)

import copy
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, final

import aiodbm
from anyio import Path


class Update:
    """Methods for updating documents."""

    @final
    @staticmethod
    async def _task_update(
        filter_fn: Callable,
        branch_number: int,
        hash_reduce_left: int,
        db_root: str,
        class_model: Any,
        mode: int,
        new_data: dict[str, Any],
    ) -> int:
        """Asynchronous task for find documents.

        This method is for internal use.

        Returns:
            The number of updated documents.
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
                        for field_name, value in new_data.items():
                            doc.__dict__[field_name] = value
                        await leaf_db.set(key, doc.model_dump_json())
                        counter += 1
        return counter

    @final
    async def update_many(
        self,
        new_data: dict[str, Any],
        filter_fn: Callable = lambda _: True,
    ) -> int:
        """Asynchronous method for updates one or more documents matching the filter.

        Attention:
            - For a complex case, a custom task may be needed.
            - See documentation on creating custom tasks.
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
            new_data (dict[str, Any]): New data for the fields that need to be updated.

        Returns:
            The number of updated documents.
        """
        # Variable initialization
        hash_reduce_left: int = self._hash_reduce_left
        assert hash_reduce_left != 0, "Scruby.run(hash_reduce_left = 0) - Not valid for `update_many` method."

        update_task_fn: Callable = self._task_update
        branch_numbers: range = range(self._max_number_branch)
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: Any = self._class_model
        mode = self._mode
        counter: int = 0

        # Run quantum loop
        with ThreadPoolExecutor(self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(
                    update_task_fn,
                    filter_fn,
                    branch_number,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    mode,
                    copy.deepcopy(new_data),
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                counter += await future.result()
        return counter
