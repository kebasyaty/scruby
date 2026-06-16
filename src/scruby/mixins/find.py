# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Quantum methods for searching documents."""

from __future__ import annotations

__all__ = ("Find",)

import warnings
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from enum import Enum
from threading import Event
from typing import Any, Never, assert_never, final

from scruby.cache import DocCache


class ReturnType(Enum):
    """Return type.

    Members:
        - `MODEL:` ScrubyModel type.
        - `JSON:` JSON-string type.
        - `DICT:` Dictionary type.
    """

    MODEL = 1
    JSON = 2
    DICT = 3


class Find:
    """Quantum methods for searching documents."""

    @final
    @staticmethod
    def _task_find(
        branch_number: int,
        filter_fn: Callable,
        hash_reduce_left: int,
        class_model: Any,
        stop_event: Event,
    ) -> list[Any] | None:
        """Task for find documents.

        This method is for internal use.

        Returns:
            List of documents or None.
        """
        # Suppress warning - RuntimeWarning: coroutine 'Find._task_find' was never awaited
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        # Variable initialization
        collection_name = class_model.__name__
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        docs: dict[str, Any] = {}
        result: list[Any] = []

        match hash_reduce_left:
            case 7:
                docs = DocCache.cache[collection_name][branch_number_as_hash[0]]
            case 6:
                docs = DocCache.cache[collection_name][branch_number_as_hash[0]][branch_number_as_hash[1]]
            case 5:
                docs = DocCache.cache[collection_name][branch_number_as_hash[0]][branch_number_as_hash[1]][
                    branch_number_as_hash[2]
                ]
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

        for _, doc in docs.items():
            if stop_event.is_set():
                return None
            if filter_fn(doc):
                result.append(doc)
        return result or None

    @final
    def find_one(
        self,
        filter_fn: Callable,
        return_type: ReturnType = ReturnType.MODEL,
    ) -> Any | None:
        """Synchronous method for find one document matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
            return_type (ReturnType): ScrubyModel, JSON-string or Dictionary.

        Returns:
            Document or None.
        """
        # Variable initialization
        hash_reduce_left: int = self._hash_reduce_left
        assert hash_reduce_left != 0, "Scruby.run(hash_reduce_left = 0) - Not valid for `find_one` method"

        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(self._max_number_branch)
        class_model: Any = self._class_model
        stop_signal = Event()
        doc: Any | None = None

        # Run quantum loop
        with ThreadPoolExecutor(self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    class_model,
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                docs = future.result()
                if docs is not None:
                    # Get first document
                    doc = docs[0]
                    # Cancel all pending tasks in the queue instantly
                    executor.shutdown(wait=False, cancel_futures=True)
                    # Trigger the event to tell running tasks to exit
                    stop_signal.set()
                    # Stop loop
                    break
        # Return document
        match return_type.value:
            case 1:
                return doc
            case 2:
                return doc.model_dump_json() if doc is not None else None
            case 3:
                return doc.model_dump() if doc is not None else None
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @final
    def find_many(
        self,
        filter_fn: Callable = lambda _: True,
        limit_docs: int = 100,
        page_number: int = 1,
        sort_fn: Callable | None = lambda doc: doc.created_at,
        sort_reverse: bool = True,
        return_type: ReturnType = ReturnType.MODEL,
    ) -> list[Any] | str | None:
        """Synchronous method for find many documents matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
                                  By default, it searches all documents.
            limit_docs (int): Limiting the number of documents.
                              Default = 100.
            page_number (int): For pagination.
                               Default = 1.
                               Number of documents per page = limit_docs.
            sort_fn (Callable | None): Sort the list of documents.
                                       By default, documents are sorted by creation date.
            sort_reverse: (bool): Sorting direction.
                                  By default, sort descending (newest to oldest).
            return_type (ReturnType): ScrubyModel, JSON-string or Dictionary.

        Returns:
            Document list or None.
        """
        if __debug__:
            if limit_docs <= 0:
                msg = "`find_many` => The `limit_docs` parameter must not be less than one."
                raise AssertionError(msg)
            if page_number <= 0:
                msg = "`find_many` => The `page_number` parameter must not be less than one."
                raise AssertionError(msg)
        # Variable initialization
        hash_reduce_left: int = self._hash_reduce_left
        assert hash_reduce_left != 0, "Scruby.run(hash_reduce_left = 0) - Not valid for `find_many` method"

        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(self._max_number_branch)
        class_model: Any = self._class_model
        stop_signal = Event()
        stop_outer_loop: bool = False
        counter: int = 0
        number_docs_skippe: int = limit_docs * (page_number - 1) if page_number > 1 else 0
        result: list[Any] = []

        # Run quantum loop
        with ThreadPoolExecutor(self._max_workers) as executor:
            futures: list[Future] = [
                executor.submit(
                    search_task_fn,
                    branch_number,
                    filter_fn,
                    hash_reduce_left,
                    class_model,
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                docs = future.result()
                if docs is not None:
                    for doc in docs:
                        if number_docs_skippe == 0:
                            if counter >= limit_docs:
                                # Cancel all pending tasks in the queue instantly
                                executor.shutdown(wait=False, cancel_futures=True)
                                # Trigger the event to tell running tasks to exit
                                stop_signal.set()
                                # Stop loops
                                stop_outer_loop = True
                                break
                            result.append(doc)
                            counter += 1
                        else:
                            number_docs_skippe -= 1
                if stop_outer_loop:
                    break
        # Sorting
        if sort_fn is not None:
            result.sort(key=sort_fn, reverse=sort_reverse)
        # Return a document list
        match return_type.value:
            case 1:
                return result or None
            case 2:
                return f"[{','.join([doc.model_dump_json() for doc in result])}]" if result is not None else None
            case 3:
                return [doc.model_dump() for doc in result] if result is not None else None
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]
