# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Database settings.

The settings class contains the following parameters:

- `db_id` - Database ID.
- `db_root` - Path to root directory of database. `Default = "ScrubyDB" (in root of project)`.
- `HASH_REDUCE_LEFT` - The length of the hash reduction on the left side.
    - `7` - 16 branches in collection (is default).
    - `6` - 256 branches in collection.
    - `5` - 4096 branches in collection.
    - `0` - 4294967296 branches in collection.
- `MAX_NUMBER_BRANCH` - Maximum number of branches in a collection.
- `max_workers` - The maximum number of processes that can be used (default = None).
- `plugins` - For adding plugins.
- `sys_platform` - Information about the operating system.
- `mode` - Access mode to directories and files.
"""

from __future__ import annotations

__all__ = ("ScrubyConfig",)

import sys
from typing import Any, ClassVar, Literal, Never, assert_never, final
from uuid import uuid4

from scruby.utils import Utils


@final
class ScrubyConfig:
    """Database settings."""

    # Database ID.
    # Will be automatically assigned.
    db_id: ClassVar[str | None] = None

    # Path to root directory of database.
    # By default = "ScrubyDB" (in root of project).
    db_root: ClassVar[str] = "ScrubyDB"

    # The length of the hash reduction on the left side.
    # 7 = 16 branches in collection.
    # 6 = 256 branches in collection (is default).
    # 5 = 4096 branches in collection.
    # 0 = 4294967296 branches in collection.
    HASH_REDUCE_LEFT: ClassVar[Literal[7, 6, 5, 0]] = 7

    # Maximum number of branches in a collection.
    # 16**(8 - HASH_REDUCE_LEFT) = 16 | 256 | 4096 | 4294967296
    MAX_NUMBER_BRANCH: ClassVar[Literal[16, 256, 4096, 4294967296]] = 16

    # The maximum number of processes that can be used to execute the given calls.
    # If None, then as many worker processes will be
    # created as the machine has processors.
    max_workers: ClassVar[int | None] = None

    # For adding plugins.
    plugins: ClassVar[list[Any] | None] = None

    # Information about the operating system.
    sys_platform: ClassVar[str] = sys.platform  # "linux", "win32", "cygwin", "darwin", "os2", "os2emx"

    # Access mode to directories and files.
    mode: ClassVar[int] = 0o777

    @classmethod
    def init_params(cls) -> None:
        """Method for general initialization of parameters."""
        cls.init_db_id()
        cls.init_max_number_branch()

    @classmethod
    def init_db_id(cls) -> None:
        """Initialize the `db_id` parameter from `db_root/.env.meta`."""
        key = "db_id"
        delimiter: str = "/" if cls.sys_platform != "win32" else ""
        dotenv_path: str = f"{cls.db_root}{delimiter}.env.meta"

        db_id: str | None = Utils.get_from_env(
            key=key,
            dotenv_path=dotenv_path,
        ) or Utils.add_to_env(
            key=key,
            value=str(uuid4())[:8],
            dotenv_path=dotenv_path,
        )

        if db_id is None:
            raise ValueError("The `db_id` parameter is missing in the `.env.meta` of the database.")

        cls.db_id = db_id

    @classmethod
    def init_max_number_branch(cls) -> None:
        """Initialize the `MAX_NUMBER_BRANCH` parameter.

        Get maximum number of branches.
        """
        match cls.HASH_REDUCE_LEFT:
            case 7:
                cls.MAX_NUMBER_BRANCH = 16
            case 6:
                cls.MAX_NUMBER_BRANCH = 256
            case 5:
                cls.MAX_NUMBER_BRANCH = 4096
            case 0:
                cls.MAX_NUMBER_BRANCH = 4294967296
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @classmethod
    def check_hash_reduce_left(cls) -> None:
        """The value of the `HASH_REDUCE_LEFT` parameter must match the value in the `.env.meta` of the database."""
        key = "hash_reduce_left"
        delimiter: str = "/" if cls.sys_platform != "win32" else ""
        dotenv_path: str = f"{cls.db_root}{delimiter}.env.meta"

        hash_reduce_left: str | None = Utils.get_from_env(
            key=key,
            dotenv_path=dotenv_path,
        ) or Utils.add_to_env(
            key=key,
            value=str(cls.HASH_REDUCE_LEFT),
            dotenv_path=dotenv_path,
        )

        if hash_reduce_left is None:
            raise ValueError("The `hash_reduce_left` parameter is missing in the `.env.meta` of the database.")

        if int(hash_reduce_left) != cls.HASH_REDUCE_LEFT:
            msg = (
                f"Scruby.run(hash_reduce_left = {cls.HASH_REDUCE_LEFT}) "
                + f"is not equal to the primary value {hash_reduce_left}."
            )
            raise ValueError(msg)

    @classmethod
    def restore(cls) -> None:
        """Restore default parameter values."""
        cls.db_id = None
        cls.db_root = "ScrubyDB"
        cls.HASH_REDUCE_LEFT = 7
        cls.MAX_NUMBER_BRANCH = 16
        cls.max_workers = None
        cls.plugins = None
        cls.sys_platform = sys.platform
