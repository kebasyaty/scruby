# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
"""Creation and management of the database."""

from __future__ import annotations

__all__ = (
    "Scruby",
    "ScrubyModel",
)

import contextlib
import logging
import re
import zlib
from datetime import datetime
from shutil import rmtree
from typing import Any, Literal, Never, assert_never

from anyio import Path
from pydantic import BaseModel

from scruby import mixins, settings


class _Meta(BaseModel):
    """Metadata of Collection."""

    db_root: str
    collection_name: str
    hash_reduce_left: int
    max_branch_number: int
    counter_documents: int


class ScrubyModel(BaseModel):
    """Additional fields for models."""

    created_at: datetime | None = None
    updated_at: datetime | None = None


class Scruby(
    mixins.Keys,
    mixins.Find,
    mixins.CustomTask,
    mixins.Collection,
    mixins.Count,
    mixins.Delete,
    mixins.Update,
):
    """Creation and management of database."""

    def __init__(  # noqa: D107
        self,
    ) -> None:
        super().__init__()
        self._meta = _Meta
        self._db_root = settings.DB_ROOT
        self._hash_reduce_left = settings.HASH_REDUCE_LEFT
        self._max_workers = settings.MAX_WORKERS
        # The maximum number of branches.
        match self._hash_reduce_left:
            case 0:
                self._max_number_branch = 4294967296
            case 2:
                self._max_number_branch = 16777216
            case 4:
                self._max_number_branch = 65536
            case 6:
                self._max_number_branch = 256
            case _ as unreachable:
                msg: str = f"{unreachable} - Unacceptable value for HASH_REDUCE_LEFT."
                logging.critical(msg)
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @classmethod
    async def collection(cls, class_model: Any) -> Any:
        """Get an object to access a collection.

        Args:
            class_model (Any): Class of Model (ScrubyModel).

        Returns:
            Instance of Scruby for access a collection.
        """
        if __debug__:
            # Check if the object belongs to the class `ScrubyModel`
            if ScrubyModel not in class_model.__bases__:
                raise AssertionError(
                    "Method: `collection` => argument `class_model` does not contain the base class `ScrubyModel`!",
                )
            # Checking the model for the presence of a key.
            model_fields = list(class_model.model_fields.keys())
            if "key" not in model_fields:
                raise AssertionError(f"Model: {class_model.__name__} => The `key` field is missing!")
            if "created_at" not in model_fields:
                raise AssertionError(f"Model: {class_model.__name__} => The `created_at` field is missing!")
            if "updated_at" not in model_fields:
                raise AssertionError(f"Model: {class_model.__name__} => The `updated_at` field is missing!")
        # Create instance of Scruby
        instance = cls()
        # Add model class to Scruby
        instance.__dict__["_class_model"] = class_model
        # Create a path for metadata.
        meta_dir_path_tuple = (
            settings.DB_ROOT,
            class_model.__name__,
            "meta",
        )
        instance.__dict__["_meta_path"] = Path(
            *meta_dir_path_tuple,
            "meta.json",
        )
        # Create metadata for collection, if missing.
        meta_dir_path = Path(*meta_dir_path_tuple)
        if not await meta_dir_path.exists():
            await meta_dir_path.mkdir(parents=True)
            meta = _Meta(
                db_root=settings.DB_ROOT,
                collection_name=class_model.__name__,
                hash_reduce_left=settings.HASH_REDUCE_LEFT,
                max_branch_number=instance.__dict__["_max_number_branch"],
                counter_documents=0,
            )
            meta_json = meta.model_dump_json()
            meta_path = Path(*(meta_dir_path, "meta.json"))
            await meta_path.write_text(meta_json, "utf-8")
        return instance

    async def get_meta(self) -> _Meta:
        """Asynchronous method for getting metadata of collection.

        This method is for internal use.

        Returns:
            Metadata object.
        """
        meta_json = await self._meta_path.read_text()
        meta: _Meta = self._meta.model_validate_json(meta_json)
        return meta

    async def _set_meta(self, meta: _Meta) -> None:
        """Asynchronous method for updating metadata of collection.

        This method is for internal use.

        Args:
            meta (_Meta): Metadata of Collection.

        Returns:
            None.
        """
        meta_json = meta.model_dump_json()
        await self._meta_path.write_text(meta_json, "utf-8")

    async def _counter_documents(self, step: Literal[1, -1]) -> None:
        """Asynchronous method for management of documents in metadata of collection.

        This method is for internal use.

        Args:
            step (Literal[1, -1]): Number of documents added or removed.

        Returns:
            None.
        """
        meta_path = self._meta_path
        meta_json = await meta_path.read_text("utf-8")
        meta: _Meta = self._meta.model_validate_json(meta_json)
        meta.counter_documents += step
        meta_json = meta.model_dump_json()
        await meta_path.write_text(meta_json, "utf-8")

    async def _get_leaf_path(self, key: str) -> tuple[Path, str]:
        """Asynchronous method for getting path to collection cell by key.

        This method is for internal use.

        Args:
            key (str): Key name.

        Returns:
            Path to cell of collection.
        """
        if not isinstance(key, str):
            msg = "The key is not a string."
            logging.error(msg)
            raise KeyError(msg)
        # Prepare key.
        # Removes spaces at the beginning and end of a string.
        # Replaces all whitespace characters with a single space.
        prepared_key = re.sub(r"\s+", " ", key).strip().lower()
        # Check the key for an empty string.
        if len(prepared_key) == 0:
            msg = "The key should not be empty."
            logging.error(msg)
            raise KeyError(msg)
        # Key to crc32 sum.
        key_as_hash: str = f"{zlib.crc32(prepared_key.encode('utf-8')):08x}"[self._hash_reduce_left :]
        # Convert crc32 sum in the segment of path.
        separated_hash: str = "/".join(list(key_as_hash))
        # The path of the branch to the database.
        branch_path: Path = Path(
            *(
                self._db_root,
                self._class_model.__name__,
                separated_hash,
            ),
        )
        # If the branch does not exist, need to create it.
        if not await branch_path.exists():
            await branch_path.mkdir(parents=True)
        # The path to the database cell.
        leaf_path: Path = Path(*(branch_path, "leaf.json"))
        return (leaf_path, prepared_key)

    @staticmethod
    def napalm() -> None:
        """Method for full database deletion.

        The main purpose is tests.

        Warning:
            - `Be careful, this will remove all keys.`

        Returns:
            None.
        """
        with contextlib.suppress(FileNotFoundError):
            rmtree(settings.DB_ROOT)
        return
