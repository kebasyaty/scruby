# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Quantum methods for running custom tasks."""

from __future__ import annotations

__all__ = ("CustomTask",)


from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from typing import Any, final


class CustomTask:
    """For running custom tasks."""

    @final
    async def run_custom_task(
        self,
        custom_task: Any,
        filter_fn: Callable = lambda _: True,
    ) -> Any:
        """For run a custom task.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            custom_task (Any): Custom task class.
            filter_fn (Callable): A function that execute the conditions of filtering.
                                  By default, it searches all documents.

        Returns:
            The result of a custom task.
        """
        hash_reduce_left: int = self._hash_reduce_left
        assert hash_reduce_left != 0, "Scruby.run(hash_reduce_left = 0) - Not valid for `run_custom_task` method."

        search_task_fn = self._task_find
        branch_numbers = range(self._max_number_branch)
        db_root = self._db_root
        class_model = self._class_model
        mode = (self._mode,)
        stop_signal = Event()
        stop_outer_loop: bool = False

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
                    mode,
                    stop_signal,
                )
                for branch_number in branch_numbers
            ]

            for future in as_completed(futures):
                docs = await future.result()

                if docs is not None:
                    for doc in docs:
                        custom_task.accept(doc)
                        if custom_task.stop_signal:
                            # Cancel all pending tasks in the queue instantly
                            executor.shutdown(wait=False, cancel_futures=True)
                            # Trigger the event to tell running tasks to exit
                            stop_signal.set()
                            # Stop loops
                            stop_outer_loop = True
                            break

                    if stop_outer_loop:
                        break

        return custom_task.result()
