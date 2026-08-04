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

import orjson
from anyio import Path


class ReturnType(Enum):
    """Return type for a find_one and find_many methods.

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
    async def _task_find(
        filter_fn: Callable,
        branch_number: int,
        hash_reduce_left: int,
        db_root: str,
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
        branch_number_as_hash: str = f"{branch_number:08x}"[hash_reduce_left:]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        leaf_path = Path(
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
                if stop_event.is_set():
                    return None
                doc = class_model.model_validate_json(val)
                if filter_fn(doc):
                    docs.append(doc)
        return docs or None

    @final
    async def find_one(
        self,
        filter_fn: Callable,
        include_fields: set[str] | None = None,
        exclude_fields: set[str] | None = None,
        return_type: ReturnType = ReturnType.MODEL,
    ) -> Any | None:
        """Asynchronous method for find one document matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
            include_fields: (set[str] | None): A set of fields to include in the output.
                                               Available for `ReturnType.JSON` and `ReturnType.DICT`.
            exclude_fields: (set[str] | None): A set of fields to exclude from the output.
                                               Available for `ReturnType.JSON` and `ReturnType.DICT`.
            return_type (ReturnType): ScrubyModel, JSON-string or Dictionary.

        Returns:
            Document or None.
        """
        # Variable initialization
        hash_reduce_left: int = self._hash_reduce_left
        assert hash_reduce_left != 0, "Scruby.run(hash_reduce_left = 0) - Not valid for `find_one` method."

        model_dump_kwargs = {"include": include_fields, "exclude": exclude_fields}
        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(self._max_number_branch)
        db_root: str = self._db_root
        class_model: Any = self._class_model
        stop_signal = Event()
        doc: Any | None = None

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
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                docs = await future.result()
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
                return doc.model_dump_json(**model_dump_kwargs) if doc is not None else None
            case 3:
                return doc.model_dump(**model_dump_kwargs) if doc is not None else None
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @final
    async def find_many(
        self,
        filter_fn: Callable = lambda _: True,
        limit_docs: int = 100,
        page_number: int = 1,
        sort_fn: Callable | None = lambda doc: doc.created_at,
        sort_reverse: bool = True,
        include_fields: set[str] | None = None,
        exclude_fields: set[str] | None = None,
        return_type: ReturnType = ReturnType.MODEL,
    ) -> list[Any] | str | None:
        """Asynchronous method for find many documents matching the filter.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            filter_fn (Callable): A function that execute the conditions of filtering.
                                  By default, it searches all documents.
            limit_docs (int): Limit the number of documents per page.
                              Default = 100.
            page_number (int): Page number (for pagination).
                               Default = 1.
                               Number of documents per page = limit_docs.
            sort_fn (Callable | None): Sort the list of documents.
                                       By default, documents are sorted by creation date.
            sort_reverse: (bool): Sorting direction.
                                  By default, sort descending (newest to oldest).
            include_fields: (set[str] | None): A set of fields to include in the output.
                                               Available for `ReturnType.JSON` and `ReturnType.DICT`.
            exclude_fields: (set[str] | None): A set of fields to exclude from the output.
                                               Available for `ReturnType.JSON` and `ReturnType.DICT`.
            return_type (ReturnType): ScrubyModel, JSON-string or Dictionary.

        Returns:
            Document list or None.
        """
        if __debug__:
            if limit_docs <= 0:
                msg = "Method: `find_many` => The `limit_docs` parameter must not be less than one."
                raise AssertionError(msg)
            if page_number <= 0:
                msg = "Method: `find_many` => The `page_number` parameter must not be less than one."
                raise AssertionError(msg)
        # Variable initialization
        hash_reduce_left: int = self._hash_reduce_left
        assert hash_reduce_left != 0, "Scruby.run(hash_reduce_left = 0) - Not valid for `find_many` method."

        model_dump_kwargs = {"include": include_fields, "exclude": exclude_fields}
        search_task_fn: Callable = self._task_find
        branch_numbers: range = range(self._max_number_branch)
        db_root: str = self._db_root
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
                    filter_fn,
                    branch_number,
                    hash_reduce_left,
                    db_root,
                    class_model,
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]
            for future in as_completed(futures):
                docs = await future.result()
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
                return (
                    f"[{','.join([doc.model_dump_json(**model_dump_kwargs) for doc in result])}]"
                    if result is not None
                    else None
                )
            case 3:
                return [doc.model_dump(**model_dump_kwargs) for doc in result] if result is not None else None
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]
