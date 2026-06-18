"""Cache documents to optimize work with the database."""

from __future__ import annotations

__all__ = ("DocCache",)


import string
from pathlib import Path
from typing import Any, ClassVar, Literal, Never, assert_never, final

import orjson

from scruby.config import ScrubyConfig
from scruby.db import _Meta


@final
class DocCache:
    """Cache documents to optimize work with the database.

    Args:
        collection_name (str): Collection name.

    Returns:
        None.
    """

    # Cache structure:
    # {"CollectionName": {"hash_symbol": {"hash_symbol": {"hash_symbol": {"key_name": doc}}}}
    cache: ClassVar[dict[str, Any]] = {}

    @staticmethod
    def create_metadata(collection_name: str) -> None:
        """Create metadata for collection.

        Args:
            collection_name (str): Collection name.

        Returns:
            None.
        """
        meta_dir_path = Path(
            ScrubyConfig.db_root,
            collection_name,
            "meta",
        )
        if not meta_dir_path.exists():
            meta_dir_path.mkdir(parents=True)
            meta = _Meta(
                collection_name=collection_name,
                hash_reduce_left=ScrubyConfig.HASH_REDUCE_LEFT,
                max_number_branch=ScrubyConfig.MAX_NUMBER_BRANCH,
                counter_documents=0,
            )
            meta_json = meta.model_dump_json()
            meta_path = Path(meta_dir_path, "meta.json")
            meta_path.write_text(meta_json, "utf-8")

    @classmethod
    def create_structure(cls, collection_name: str) -> None:
        """Create a cache structure for the collection.

        Args:
            collection_name (str): Collection name.

        Returns:
            None.
        """
        if ScrubyConfig.HASH_REDUCE_LEFT == 0:
            return

        hexdigits = string.hexdigits.lower()
        match ScrubyConfig.HASH_REDUCE_LEFT:
            case 7:
                cls.cache[collection_name] = {key: {} for key in hexdigits}
            case 6:
                cls.cache[collection_name] = {key: {key: {} for key in hexdigits} for key in hexdigits}
            case 5:
                cls.cache[collection_name] = {
                    key: {key: {key: {} for key in hexdigits} for key in hexdigits} for key in hexdigits
                }
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @classmethod
    def load_cache(cls, subclasses: list[Any]) -> None:
        """Load all documents from the database into the cache."""
        if ScrubyConfig.HASH_REDUCE_LEFT == 0:
            return

        db_root: Path = Path(ScrubyConfig.db_root)
        HASH_REDUCE_LEFT: Literal[7, 6, 5, 0] = ScrubyConfig.HASH_REDUCE_LEFT
        MAX_NUMBER_BRANCH: Literal[16, 256, 4096, 4294967296] = ScrubyConfig.MAX_NUMBER_BRANCH
        branch_numbers: range = range(MAX_NUMBER_BRANCH)

        for subclass in subclasses:
            collection_name = subclass.__name__
            cls.create_metadata(collection_name)
            cls.create_structure(collection_name)

            for branch_number in branch_numbers:
                branch_number_as_hash: str = f"{branch_number:08x}"[HASH_REDUCE_LEFT:]
                separated_hash = "/".join(list(branch_number_as_hash))
                leaf_path = Path(
                    *(
                        db_root,
                        collection_name,
                        separated_hash,
                        "leaf.json",
                    ),
                )

                if leaf_path.exists():
                    data_json: bytes = leaf_path.read_bytes()
                    data: dict[str, str] = orjson.loads(data_json) or {}
                    for key, val in data.items():
                        doc = subclass.model_validate_json(val)
                        match HASH_REDUCE_LEFT:
                            case 7:
                                cls.cache[collection_name][branch_number_as_hash[0]][key] = doc
                            case 6:
                                cls.cache[collection_name][branch_number_as_hash[0]][branch_number_as_hash[1]][key] = (
                                    doc
                                )
                            case 5:
                                cls.cache[collection_name][branch_number_as_hash[0]][branch_number_as_hash[1]][
                                    branch_number_as_hash[2]
                                ][key] = doc
                            case _ as unreachable:
                                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]
