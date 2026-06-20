"""Cache documents to optimize work with the database."""

from __future__ import annotations

__all__ = ("DocCache",)


import string
from pathlib import Path
from typing import Any, ClassVar, Literal, Never, assert_never, final

import orjson

from scruby.config import ScrubyConfig
from scruby.meta import Metadata


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

    @classmethod
    def create_structure(cls, collection_name: str) -> None:
        """Create structure of empty cache for collection.

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
        db_root: Path = Path(ScrubyConfig.db_root)
        HASH_REDUCE_LEFT: Literal[7, 6, 5, 0] = ScrubyConfig.HASH_REDUCE_LEFT
        MAX_NUMBER_BRANCH: Literal[16, 256, 4096, 4294967296] = ScrubyConfig.MAX_NUMBER_BRANCH
        branch_numbers: range = range(MAX_NUMBER_BRANCH)

        for subclass in subclasses:
            collection_name: str = subclass.__name__

            # Create metadata for the collection if it is missing
            Metadata.create(collection_name)

            if HASH_REDUCE_LEFT == 0:
                continue

            # Create a cache structure for the collection
            cls.create_structure(collection_name)

            # Get data from database and add to cache for collection
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
