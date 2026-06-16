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
from typing import Any, Literal, final

from anyio import Path
from pydantic import BaseModel
from xloft import NamedTuple

from scruby import mixins
from scruby.cache import DocCache
from scruby.config import ScrubyConfig


class _Meta(BaseModel):
    """Metadata of Collection."""

    collection_name: str
    hash_reduce_left: int
    max_number_branch: int
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
        self._db_root = ScrubyConfig.db_root
        self._db_id = ScrubyConfig.db_id
        self._max_workers = ScrubyConfig.max_workers

    @classmethod
    async def collection(cls, class_model: Any) -> Any:
        """Asynchronous method for creating a new collection and accessing an existing collection.

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
            len_db_root_absolut_path = len(str(await Path(ScrubyConfig.db_root).resolve()).encode("utf-8"))
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
            ScrubyConfig.db_root,
            class_model.__name__,
            "meta",
        )
        instance.__dict__["_meta_path"] = Path(
            *meta_dir_path_tuple,
            "meta.json",
        )
        # Create metadata for collection, if missing.
        meta_dir_path = Path(*meta_dir_path_tuple)
        if await meta_dir_path.exists():
            # Get metadata if it already exists.
            meta_json = await instance.__dict__["_meta_path"].read_text()
            meta: _Meta = instance.__dict__["_meta"].model_validate_json(meta_json)
            instance.__dict__["_hash_reduce_left"] = meta.hash_reduce_left
            instance.__dict__["_max_number_branch"] = meta.max_number_branch
        else:
            instance.__dict__["_hash_reduce_left"] = ScrubyConfig.HASH_REDUCE_LEFT
            instance.__dict__["_max_number_branch"] = ScrubyConfig.MAX_NUMBER_BRANCH
            # Create metadata.
            await meta_dir_path.mkdir(parents=True)
            meta = _Meta(
                collection_name=class_model.__name__,
                hash_reduce_left=ScrubyConfig.HASH_REDUCE_LEFT,
                max_number_branch=ScrubyConfig.MAX_NUMBER_BRANCH,
                counter_documents=0,
            )
            # Save metadata to database.
            meta_json = meta.model_dump_json()
            meta_path = Path(*(meta_dir_path, "meta.json"))
            await meta_path.write_text(meta_json, "utf-8")
            # Create a cache structure for the collection.
            DocCache.create_structure(class_model.__name__)
        # Plugins connection.
        plugin_list: dict[str, Any] = {}
        if ScrubyConfig.plugins is not None:
            for plugin in ScrubyConfig.plugins:
                name = plugin.__name__
                name = name[0].lower() + name[1:]
                plugin_list[name] = plugin(scruby_self=instance)
        instance.__dict__["plugins"] = NamedTuple(**plugin_list)
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

    async def _get_leaf_path(self, key: str) -> tuple[Path, str, str]:
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
        # Get the path to the collection cell.
        leaf_path: Path = Path(*(branch_path, "leaf.json"))
        return (leaf_path, prepared_key, key_as_hash)

    @staticmethod
    def napalm() -> None:
        """Method for full database deletion.

        The main purpose is tests.

        Warning:
            - `Be careful, this will remove all keys.`

        Returns:
            None.
        """
        DocCache.cache = {}
        with contextlib.suppress(FileNotFoundError):
            rmtree(ScrubyConfig.db_root)
        return

    @staticmethod
    def run(
        db_root: str = "ScrubyDB",
        hash_reduce_left: Literal[7, 6, 5, 0] = 7,
        max_workers: int | None = None,
        plugins: list[Any] | None = None,
    ) -> None:
        """Activate database.

        Args:
            db_root (str): Path to root directory of database.
                           Default = "ScrubyDB" (in root of project).
            max_workers (int | None ): The maximum number of processes that can be used to execute the given calls.
                                       If None, then as many worker processes will be
                                       created as the machine has processors.
            plugins (list[Any] | None): To connect plugins.

        Returns:
            None.
        """
        if __debug__ and plugins is not None:
            for plugin in plugins:
                if plugin.SCRUBY_VERSION != 2:
                    msg = f"Plugin {plugin.__name__} does not apply to version 2."
                    raise AssertionError(msg)

        ScrubyConfig.db_root = db_root
        ScrubyConfig.HASH_REDUCE_LEFT = hash_reduce_left
        ScrubyConfig.max_workers = max_workers
        ScrubyConfig.plugins = plugins
        ScrubyConfig.init_params()
        DocCache.load_cache(ScrubyModel.__subclasses__())
