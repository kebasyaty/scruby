"""Creation and management of the database."""

from __future__ import annotations

__all__ = ("Scruby",)

import contextlib
import logging
import re
import zlib
from shutil import rmtree
from typing import Any, Literal, Never, assert_never

from anyio import Path
from pydantic import BaseModel

from scruby import constants, mixins

logger = logging.getLogger(__name__)


class _Meta(BaseModel):
    """Metadata of Collection."""

    db_root: str
    collection_name: str
    hash_reduce_left: int
    max_branch_number: int
    counter_documents: int


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
        self._db_root = constants.DB_ROOT
        self._hash_reduce_left = constants.HASH_REDUCE_LEFT
        # The maximum number of branches.
        match self._hash_reduce_left:
            case 0:
                self._max_branch_number = 4294967296
            case 2:
                self._max_branch_number = 16777216
            case 4:
                self._max_branch_number = 65536
            case 6:
                self._max_branch_number = 256
            case _ as unreachable:
                msg: str = f"{unreachable} - Unacceptable value for HASH_REDUCE_LEFT."
                logger.critical(msg)
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @classmethod
    async def create(cls, class_model: Any) -> Any:
        """Get an object to access a collection.

        Args:
            class_model: Class of Model (pydantic.BaseModel).

        Returns:
            Instance of Scruby for access a collection.
        """
        assert BaseModel in class_model.__bases__, "`class_model` does not contain the base class `pydantic.BaseModel`!"
        instance = cls()
        instance.__dict__["_class_model"] = class_model
        # Caching a pati for metadata.
        # The zero branch is reserved for metadata.
        branch_number: int = 0
        branch_number_as_hash: str = f"{branch_number:08x}"[constants.HASH_REDUCE_LEFT :]
        separated_hash: str = "/".join(list(branch_number_as_hash))
        meta_dir_path_tuple = (
            constants.DB_ROOT,
            class_model.__name__,
            separated_hash,
        )
        instance.__dict__["_meta_path"] = Path(
            *meta_dir_path_tuple,
            "meta.json",
        )
        # Create metadata for collection, if missing.
        branch_path = Path(*meta_dir_path_tuple)
        if not await branch_path.exists():
            await branch_path.mkdir(parents=True)
            meta = _Meta(
                db_root=constants.DB_ROOT,
                collection_name=class_model.__name__,
                hash_reduce_left=constants.HASH_REDUCE_LEFT,
                max_branch_number=instance.__dict__["_max_branch_number"],
                counter_documents=0,
            )
            meta_json = meta.model_dump_json()
            meta_path = Path(*(branch_path, "meta.json"))
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

        Returns:
            None.
        """
        meta_json = meta.model_dump_json()
        await self._meta_path.write_text(meta_json, "utf-8")

    async def _counter_documents(self, step: Literal[1, -1]) -> None:
        """Asynchronous method for management of documents in metadata of collection.

        This method is for internal use.

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
            logger.error(msg)
            raise KeyError(msg)
        # Prepare key.
        # Removes spaces at the beginning and end of a string.
        # Replaces all whitespace characters with a single space.
        prepared_key = re.sub(r"\s+", " ", key).strip().lower()
        # Check the key for an empty string.
        if len(prepared_key) == 0:
            msg = "The key should not be empty."
            logger.error(msg)
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
            rmtree(constants.DB_ROOT)
        return
