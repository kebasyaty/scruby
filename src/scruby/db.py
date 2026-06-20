# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Creation and management of the database."""

from __future__ import annotations

__all__ = ("Scruby",)

import contextlib
import re
import zlib
from shutil import rmtree
from typing import Any, Literal, final

from anyio import Path
from xloft import NamedTuple

from scruby import mixins
from scruby.cache import DocCache
from scruby.config import ScrubyConfig
from scruby.meta import Meta
from scruby.model import ScrubyModel


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
        class_model: Any,
    ) -> None:
        if __debug__:
            if ScrubyModel not in class_model.__bases__:
                msg = "Scruby => Argument `class_model` does not contain the base class `ScrubyModel`."
                raise AssertionError(msg)
            if "key" not in list(class_model.model_fields.keys()):
                msg = f"Model: {class_model.__name__} => The `key` field is missing."
                raise AssertionError(msg)

        super().__init__()
        self._class_model = class_model
        self._db_id = ScrubyConfig.db_id
        self._db_root = ScrubyConfig.db_root
        self._hash_reduce_left = ScrubyConfig.HASH_REDUCE_LEFT
        self._max_number_branch = ScrubyConfig.MAX_NUMBER_BRANCH
        self._max_workers = ScrubyConfig.max_workers
        self._meta = Meta
        self._meta_path = Path(
            ScrubyConfig.db_root,
            class_model.__name__,
            "meta",
            "meta.json",
        )
        # Plugins connection.
        plugin_list: dict[str, Any] = {}
        if ScrubyConfig.plugins is not None:
            for plugin in ScrubyConfig.plugins:
                name = plugin.__name__
                name = name[0].lower() + name[1:]
                plugin_list[name] = plugin(scruby_self=self)
        self.plugins = NamedTuple(**plugin_list)

    async def get_meta(self) -> Meta:
        """Asynchronous method for getting metadata of collection.

        This method is for internal use.

        Returns:
            Metadata object.
        """
        meta_json = await self._meta_path.read_text()
        meta: Meta = self._meta.model_validate_json(meta_json)
        return meta

    async def _set_meta(self, meta: Meta) -> None:
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
        meta: Meta = self._meta.model_validate_json(meta_json)
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
        ScrubyConfig.restore()
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
        subclasses: list[Any] = ScrubyModel.__subclasses__()
        if __debug__:
            if len(subclasses) == 0:
                raise AssertionError("Create least one model of document for your project.")
            if plugins is not None:
                for plugin in plugins:
                    if plugin.SCRUBY_VERSION != 2:
                        msg = f"Plugin {plugin.__name__} does not apply to version 2."
                        raise AssertionError(msg)

        ScrubyConfig.db_root = db_root
        ScrubyConfig.HASH_REDUCE_LEFT = hash_reduce_left
        ScrubyConfig.max_workers = max_workers
        ScrubyConfig.plugins = plugins
        ScrubyConfig.init_params()
        ScrubyConfig.check_hash_reduce_left()
        DocCache.load_cache(subclasses)
