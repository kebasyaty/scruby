"""Quantum methods for running custom tasks."""

from __future__ import annotations

__all__ = ("CustomTask",)

import logging
from collections.abc import Callable
from typing import Any, TypeVar

import orjson
from anyio import Path

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CustomTask[T]:
    """Quantum methods for running custom tasks."""

    @staticmethod
    async def _task_get_docs(
        branch_number: int,
        hash_reduce_left: int,
        db_root: str,
        class_model: T,
    ) -> list[Any]:
        """Get documents for custom task.

        This method is for internal use.

        Returns:
            List of documents.
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
        docs: list[Any] = []
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                docs.append(class_model.model_validate_json(val))
        return docs

    async def run_custom_task(self, custom_task_fn: Callable, limit_docs: int = 1000) -> Any:
        """Running custom task.

        This method running a task created on the basis of a quantum loop.
        Effectiveness running task depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            custom_task_fn: A function that execute the custom task.
            limit_docs: Limiting the number of documents. By default = 1000.

        Returns:
            The result of a custom task.
        """
        kwargs = {
            "get_docs_fn": self._task_get_docs,
            "branch_numbers": range(1, self._max_branch_number),
            "hash_reduce_left": self._hash_reduce_left,
            "db_root": self._db_root,
            "class_model": self._class_model,
            "limit_docs": limit_docs,
        }
        return await custom_task_fn(**kwargs)
