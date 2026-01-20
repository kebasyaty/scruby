# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Creation and management of the database."""

from __future__ import annotations

__all__ = (
    "Scruby",
    "ScrubyModel",
)

import contextlib
import re
import zlib
from datetime import datetime
from shutil import rmtree
from typing import Any, Literal, Never, assert_never, final

from anyio import Path
from pydantic import BaseModel
from xloft import NamedTuple

from scruby import mixins
from scruby.settings import ScrubySettings


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


@final
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
        self._db_root = ScrubySettings.db_root
        self._hash_reduce_left = ScrubySettings.hash_reduce_left
        self._max_workers = ScrubySettings.max_workers
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
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]
        # Plugins connection.
        plugin_list: dict[str, Any] = {}
        for plugin in ScrubySettings.plugins:
            name = plugin.__name__
            name = name[0].lower() + name[1:]
            plugin_list[name] = plugin(scruby=self)
        self.plugins = NamedTuple(**plugin_list)

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
                msg = (
                    "Method: `collection` => argument `class_model` " + "does not contain the base class `ScrubyModel`!"
                )
                raise AssertionError(msg)
            # Checking the model for the presence of a key.
            model_fields = list(class_model.model_fields.keys())
            if "key" not in model_fields:
                msg = f"Model: {class_model.__name__} => The `key` field is missing!"
                raise AssertionError(msg)
            if "created_at" not in model_fields:
                msg = f"Model: {class_model.__name__} => The `created_at` field is missing!"
                raise AssertionError(msg)
            if "updated_at" not in model_fields:
                msg = f"Model: {class_model.__name__} => The `updated_at` field is missing!"
                raise AssertionError(msg)
            # Check the length of the collection name for an acceptable size.
            len_db_root_absolut_path = len(str(await Path(ScrubySettings.db_root).resolve()).encode("utf-8"))
            len_model_name = len(class_model.__name__)
            len_full_path_leaf = len_db_root_absolut_path + len_model_name + 26
            if len_full_path_leaf > 255:
                excess = len_full_path_leaf - 255
                msg = (
                    f"Model: {class_model.__name__} => The collection name is too long, "
                    + f"it exceeds the limit of {excess} characters!"
                )
                raise AssertionError(msg)
        # Create instance of Scruby
        instance = cls()
        # Add model class to Scruby
        instance.__dict__["_class_model"] = class_model
        # Create a path for metadata.
        meta_dir_path_tuple = (
            ScrubySettings.db_root,
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
                db_root=ScrubySettings.db_root,
                collection_name=class_model.__name__,
                hash_reduce_left=ScrubySettings.hash_reduce_left,
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
            raise KeyError("The key is not a string.")
        # Prepare key.
        # Removes spaces at the beginning and end of a string.
        # Replaces all whitespace characters with a single space.
        prepared_key = re.sub(r"\s+", " ", key).strip().lower()
        # Check the key for an empty string.
        if len(prepared_key) == 0:
            raise KeyError("The key should not be empty.")
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
            rmtree(ScrubySettings.db_root)
        return
