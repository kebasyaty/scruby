"""Methods for updating documents."""

from __future__ import annotations

__all__ = ("Update",)

import concurrent.futures
import logging
from collections.abc import Callable
from typing import Any, TypeVar

import orjson
from anyio import Path

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Update[T]:
    """Methods for updating documents."""

    @staticmethod
    async def _task_update(
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
            for _, val in data.items():
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    for key, value in new_data.items():
                        doc.__dict__[key] = value
                        new_state[key] = doc.model_dump_json()
                    counter += 1
            await leaf_path.write_bytes(orjson.dumps(new_state))
        return counter

    async def update_many(
        self,
        filter_fn: Callable,
        new_data: dict[str, Any],
        max_workers: int | None = None,
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

        Returns:
            The number of updated documents.
        """
        branch_numbers: range = range(1, self._max_branch_number)
        update_task_fn: Callable = self._task_update
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: T = self._class_model
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
                counter += await future.result()
        return counter
