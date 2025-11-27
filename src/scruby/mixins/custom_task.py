"""Quantum methods for running custom tasks."""

from __future__ import annotations

__all__ = ("CustomTask",)

import logging
from collections.abc import Callable
from pathlib import Path as SyncPath
from typing import Any, TypeVar

import orjson

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CustomTask[T]:
    """Quantum methods for running custom tasks."""

    def __init__(  # noqa: D107
        self,
        db_root: str,
        hash_reduce_left: int,
        max_branch_number: int,
        class_model: T,
    ) -> None:
        self.__db_root = db_root
        self.__hash_reduce_left = hash_reduce_left
        self.__max_branch_number = max_branch_number
        self.__class_model = class_model

    @staticmethod
    def _task_get_docs(
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
        leaf_path: SyncPath = SyncPath(
            *(
                db_root,
                class_model.__name__,
                separated_hash,
                "leaf.json",
            ),
        )
        docs: list[str, T] = []
        if leaf_path.exists():
            data_json: bytes = leaf_path.read_bytes()
            data: dict[str, str] = orjson.loads(data_json) or {}
            for _, val in data.items():
                docs.append(class_model.model_validate_json(val))
        return docs

    def run_custom_task(self, custom_task_fn: Callable, limit_docs: int = 1000) -> Any:
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
            "branch_numbers": range(1, self.__max_branch_number),
            "hash_reduce_left": self.__hash_reduce_left,
            "db_root": self.__db_root,
            "class_model": self.__class_model,
            "limit_docs": limit_docs,
        }
        return custom_task_fn(**kwargs)
