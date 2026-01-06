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
    ) -> list[Any] | None:
        """Task for find documents.

        This method is for internal use.

        Returns:
            List of documents or None.
        """
        # Variable initialization
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
                if filter_fn(doc):
                    docs.append(doc)
        return docs or None

    async def find_one(
        self,
        filter_fn: Callable,
    ) -> Any | None:
        """Find one document matching the filter.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.

        Returns:
            Document or None.
        """
        # Variable initialization
        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(self._max_number_branch)
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: Any = self._class_model
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
                    return docs[0]
        return None

    async def find_many(
        self,
        filter_fn: Callable = lambda _: True,
        limit_docs: int = 1000,
        page_number: int = 1,
    ) -> list[Any] | None:
        """Find many documents matching the filter.

        The search is based on the effect of a quantum loop.
        The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
                                  By default it searches for all documents.
            limit_docs (int): Limiting the number of documents. By default = 1000.
            page_number (int): For pagination output. By default = 1.
                               Number of documents per page = limit_docs.

        Returns:
            List of documents or None.
        """
        # The `page_number` parameter must not be less than one
        assert page_number > 0, "`find_many` => The `page_number` parameter must not be less than one."
        # Variable initialization
        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(self._max_number_branch)
        hash_reduce_left: int = self._hash_reduce_left
        db_root: str = self._db_root
        class_model: Any = self._class_model
        counter: int = 0
        number_docs_skippe: int = limit_docs * (page_number - 1) if page_number > 1 else 0
        result: list[Any] = []
        # Run quantum loop
        with concurrent.futures.ThreadPoolExecutor(self._max_workers) as executor:
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
                )
                docs = await future.result()
                if docs is not None:
                    for doc in docs:
                        if number_docs_skippe == 0:
                            if counter >= limit_docs:
                                return result[:limit_docs]
                            result.append(doc)
                            counter += 1
                        else:
                            number_docs_skippe -= 1
        return result or None
