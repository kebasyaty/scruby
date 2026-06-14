# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for working with collections."""

from __future__ import annotations

__all__ = ("Collection",)

from shutil import rmtree
from typing import final

from anyio import Path, to_thread

from scruby.cache import DocCache
from scruby.config import ScrubyConfig


class Collection:
    """Methods for working with collections."""

    @final
    def collection_name(self) -> str:
        """Asynchronous method for getting the collection name.

        Returns:
            Collection name.
        """
        return self._class_model.__name__

    @final
    @staticmethod
    async def collection_list() -> list[str] | None:
        """Asynchronous method for getting collection list."""
        db_directory = Path(ScrubyConfig.db_root)
        # Get all entries in the directory
        all_entries = Path.iterdir(db_directory)
        directory_names: list[str] = [entry.name async for entry in all_entries if entry.name != ".env.meta"]
        return directory_names or None

    @final
    @staticmethod
    async def delete_collection(collection_name: str) -> None:
        """Asynchronous method for deleting a collection by its name.

        Args:
            collection_name (str): Collection name.

        Returns:
            None.
        """
        target_directory = f"{ScrubyConfig.db_root}/{collection_name}"
        await to_thread.run_sync(rmtree, target_directory)  # pyrefly: ignore [bad-argument-type, incompatible-overload-residual]
        del DocCache.cache[collection_name]
        return
