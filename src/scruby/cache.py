"""Cache documents to optimize work with the database."""

from __future__ import annotations

__all__ = ("DocCache",)

import string
from pathlib import Path
from typing import Any, ClassVar, Literal, final

import orjson

from scruby.config import ScrubyConfig


@final
class DocCache:
    """Cache documents to optimize work with the database."""

    # Cache structure:
    # {"CollectionName": {"hash_symbol": {"hash_symbol": {"hash_symbol": {"key_name": doc}}}}
    cache: ClassVar[dict[str, Any]] = {}

    @classmethod
    def create_structure(cls, collection_name: str) -> None:
        """Create a cache structure for the collection."""
        hexdigits = string.hexdigits.lower()
        cls.cache[collection_name] = {
            key0: {key1: {key2: {} for key2 in hexdigits} for key1 in hexdigits} for key0 in hexdigits
        }

    @classmethod
    def load_cache(cls, subclasses: list[Any]) -> None:
        """Load all documents from the database into the cache."""
        db_root: Path = Path(ScrubyConfig.db_root)
        HASH_REDUCE_LEFT: Literal[5] = ScrubyConfig.HASH_REDUCE_LEFT
        MAX_NUMBER_BRANCH: Literal[4096] = 4096
        branch_numbers: range = range(MAX_NUMBER_BRANCH)

        # Leave function if database does not exist
        if not db_root.exists():
            return

        for subclass in subclasses:
            collection_name = subclass.__name__
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
                    separated_hash = branch_number_as_hash.split()
                    data_json: bytes = leaf_path.read_bytes()
                    data: dict[str, str] = orjson.loads(data_json) or {}
                    for key, val in data.items():
                        doc = subclass.model_validate_json(val)
                        cls.cache[collection_name][separated_hash[0]][separated_hash[1]][separated_hash[2]][key] = doc
