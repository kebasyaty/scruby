# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Quantum methods for running custom tasks."""

from __future__ import annotations

__all__ = ("CustomTask",)

from collections.abc import Callable
from typing import Any


class CustomTask:
    """Quantum methods for running custom tasks."""

    async def run_custom_task(
        self,
        custom_task_fn: Callable,
        filter_fn: Callable = lambda _: True,
        **kwargs,
    ) -> Any:
        """For run an asynchronous custom task.

        Attention:
            - The search is based on the effect of a quantum loop.
            - The search effectiveness depends on the number of processor threads.

        Args:
            custom_task_fn (Callable): A function that execute the custom task.

        Returns:
            The result of a custom task.
        """
        return await custom_task_fn(
            search_task_fn=self._task_find,
            filter_fn=filter_fn,
            branch_numbers=range(self._max_number_branch),
            hash_reduce_left=self._hash_reduce_left,
            db_root=self._db_root,
            class_model=self._class_model,
            max_workers=self._max_workers,
            **kwargs,
        )
