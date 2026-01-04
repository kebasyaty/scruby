# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
#
"""Quantum methods for searching documents."""

from __future__ import annotations

__all__ = ("Find",)

import concurrent.futures
from collections.abc import Callable
from typing import Any

import orjson
from anyio import Path


class Find:
    """Quantum methods for searching documents."""

    @staticmethod
    async def _task_find(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: str,
        db_root: str,
        class_model: Any,
        filter_is_checking: bool = True,
    ) -> list[Any] | None:
        """Task for find documents.

        This method is for internal use.

        Returns:
            List of documents or None.
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
                doc = class_model.model_validate_json(val)
                if not filter_is_checking or filter_fn(doc):
                    docs.append(doc)
        return docs or None

    async def find_one(
        self,
        filter_fn: Callable,
        max_workers: int | None = None,
    ) -> Any | None:
        """Finds a single document matching the filter.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
            max_workers (int): The maximum number of processes that can be used to
                               execute the given calls. If None or not given then as many
                               worker processes will be created as the machine has processors.

        Returns:
            Document or None.
        """
        branch_numbers: range = range(1, self._max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: Any = self._class_model
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
                docs = await future.result()
                if docs is not None:
                    return docs[0]
        return None

    async def find_many(
        self,
        filter_fn: Callable,
        limit_docs: int = 1000,
        page_number: int = 1,
        max_workers: int | None = None,
    ) -> list[Any] | None:
        """Finds one or more documents matching the filter.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.
        Ideally, hundreds and even thousands of threads are required.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
            limit_docs (int): Limiting the number of documents. By default = 1000.
            page_number (int): For pagination output. By default = 1.
                               Number of documents per page = limit_docs.
            max_workers (int): The maximum number of processes that can be used to
                               execute the given calls. If None or not given then as many
                               worker processes will be created as the machine has processors.

        Returns:
            List of documents or None.
        """
        branch_numbers: range = range(1, self._max_branch_number)
        search_task_fn: Callable = self._task_find
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: Any = self._class_model
        counter: int = 0
        number_docs_skippe: int = limit_docs * (page_number - 1) if page_number > 1 else 0
        result: list[Any] = []
        filter_is_checking: bool = False
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for branch_number in branch_numbers:
                if number_docs_skippe == 0 and counter >= limit_docs:
                    return result[:limit_docs]
                future = executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    filter_is_checking,
                )
                docs = await future.result()
                if docs is not None:
                    for doc in docs:
                        if number_docs_skippe == 0:
                            if counter >= limit_docs:
                                return result[:limit_docs]
                            if filter_fn(doc):
                                result.append(doc)
                                counter += 1
                        else:
                            number_docs_skippe -= 1
        return result or None
