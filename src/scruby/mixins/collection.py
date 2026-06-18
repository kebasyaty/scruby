# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for working with collections."""

from __future__ import annotations

__all__ = ("Collection",)

from shutil import rmtree
from typing import final

from scruby.cache import DocCache
from scruby.config import ScrubyConfig
from scruby.db import ScrubyModel


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
    def collection_list() -> list[str] | None:
        """Synchronous method for getting collection list."""
        collections = [item.__name__ for item in ScrubyModel.__subclasses__()]
        return collections or None

    @final
    @staticmethod
    def clear_collection(collection_name: str) -> None:
        """Synchronous method to remove all documents from a collection.

        Args:
            collection_name (str): Collection name.

        Returns:
            None.
        """
        # Clear collection on file system
        target_directory = f"{ScrubyConfig.db_root}/{collection_name}"
        rmtree(target_directory)
        # Create metadata for collection
        DocCache.create_metadata(collection_name)

        # Clear collection in cache
        if ScrubyConfig.HASH_REDUCE_LEFT != 0:
            del DocCache.cache[collection_name]
            DocCache.create_structure(collection_name)
        return
