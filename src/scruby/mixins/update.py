# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for updating documents."""

from __future__ import annotations

__all__ = ("Update",)

import concurrent.futures
import copy
from collections.abc import Callable
from pathlib import Path as SyncPath
from typing import Any

import orjson


class Update:
    """Methods for updating documents."""

    @staticmethod
    def _task_update(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: str,
        db_root: str,
        class_model: Any,
        new_data: dict[str, Any],
    ) -> int:
        """Task for find documents.

        This method is for internal use.

        Returns:
            The number of updated documents.
        """
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        leaf_path = SyncPath(
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

    async def update_many(
        self,
        new_data: dict[str, Any],
        filter_fn: Callable = lambda _: True,
    ) -> int:
        """Updates many documents matching the filter.

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
        update_task_fn: Callable = self._task_update
        branch_numbers: range = range(self._max_number_branch)
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: Any = self._class_model
        counter: int = 0
        # Run quantum loop
        with concurrent.futures.ThreadPoolExecutor(self._max_workers) as executor:
            for branch_number in branch_numbers:
                future = executor.submit(
                    update_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    copy.deepcopy(new_data),
                )
                counter += future.result()
        return counter
