# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Database settings.

The settings class contains the following parameters:

- `db_root` - Path to root directory of database. `By default = "ScrubyDB" (in root of project)`.
- `db_id` - Database ID.
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

import uuid
from pathlib import Path
from typing import Any, ClassVar, Literal, final

from dotenv import dotenv_values


@final
class ScrubySettings:
    """Database settings."""

    # Path to root directory of database
    # By default = "ScrubyDB" (in root of project).
    db_root: ClassVar[str] = "ScrubyDB"

    # Database ID
    db_id: str = ""

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

    @classmethod
    def get_db_id(cls) -> None:
        """Get the database ID."""
        id: str | None = None
        db_meta_path: str = f"{cls.db_root}/meta/meta.env"

        if Path(db_meta_path).exists():
            meta: dict[str, str | None] = dotenv_values(db_meta_path)
            id = meta.get("id")
            if id is None:
                with Path(db_meta_path).open("a+", encoding="utf-8") as env_file:
                    id = str(uuid.uuid4())[:8]
                    content = f"\nid={id}"
                    env_file.write(content)
        else:
            id = str(uuid.uuid4())[:8]
            content = f"id={id}"
            Path(db_meta_path).write_text(data=content, encoding="utf-8")

        if id is None:
            raise ValueError("Failed attempt to obtain database ID.")

        cls.db_id = id


ScrubySettings.get_db_id()
