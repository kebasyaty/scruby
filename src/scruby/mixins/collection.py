# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for working with collections."""

from __future__ import annotations

__all__ = ("Collection",)

from shutil import rmtree
from typing import final

from scruby.config import ScrubyConfig
from scruby.meta import Metadata
from scruby.models import ScrubyModel


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
    @classmethod
    def clear_collection(cls, collection_name: str) -> None:
        """Synchronous method to remove all documents from a collection.

        Args:
            collection_name (str): Collection name.

        Returns:
            None.
        """
        db_root = ScrubyConfig.db_root
        hash_reduce_left = ScrubyConfig.HASH_REDUCE_LEFT
        max_number_branch = ScrubyConfig.MAX_NUMBER_BRANCH

        # Delete collection on file system
        target_directory = f"{db_root}/{collection_name}"
        rmtree(target_directory)

        # Create a directory for the collection and add metadata
        Metadata.create(
            db_root,
            hash_reduce_left,
            max_number_branch,
            collection_name,
        )

        return
