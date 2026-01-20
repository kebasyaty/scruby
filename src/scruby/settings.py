# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Database settings.

The settings class contains the following parameters:

- `db_root` - Path to root directory of database. `By default = "ScrubyDB" (in root of project)`.
- `hash_reduce_left` - The length of the hash reduction on the left side.
    - `0` - 4294967296 branches in collection.
    - `2` - 16777216 branches in collection.
    - `4` - 65536 branches in collection.
    - `6` - 256 branches in collection (by default).
- `max_workers` - The maximum number of processes that can be used `By default = None`.
- `plugins` - For adding plugins.
"""

from __future__ import annotations

__all__ = ("ScrubySettings",)

from typing import Any, ClassVar, Literal, final


@final
class ScrubySettings:
    """Database settings."""

    # Path to root directory of database
    # By default = "ScrubyDB" (in root of project).
    db_root: ClassVar[str] = "ScrubyDB"

    # The length of the hash reduction on the left side.
    # 0 = 4294967296 branches in collection.
    # 2 = 16777216 branches in collection.
    # 4 = 65536 branches in collection.
    # 6 = 256 branches in collection (by default).
    # Number of branches is number of requests to the hard disk during quantum operations.
    # Quantum operations: find_one, find_many, count_documents, delete_many, run_custom_task.
    hash_reduce_left: ClassVar[Literal[0, 2, 4, 6]] = 6

    # The maximum number of processes that can be used to execute the given calls.
    # If None, then as many worker processes will be
    # created as the machine has processors.
    max_workers: ClassVar[int | None] = None

    # For adding plugins.
    plugins: ClassVar[list[Any]] = []
