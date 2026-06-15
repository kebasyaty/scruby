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
        match ScrubyConfig.HASH_REDUCE_LEFT:
            case 7:
                cls.cache[collection_name] = {key: {} for key in hexdigits}
            case 6:
                cls.cache[collection_name] = {key: {key: {} for key in hexdigits} for key in hexdigits}
            case 5:
                cls.cache[collection_name] = {
                    key: {key: {key: {} for key in hexdigits} for key in hexdigits} for key in hexdigits
                }
            case _:
                msg = "Scruby.run() > Parameter: `hash_reduce_left` -> Valid values are Literal[7, 6, 5]."
                raise AssertionError(msg)

    @classmethod
    def load_cache(cls, subclasses: list[Any]) -> None:
        """Load all documents from the database into the cache."""
        db_root: Path = Path(ScrubyConfig.db_root)
        HASH_REDUCE_LEFT: Literal[7, 6, 5] = ScrubyConfig.HASH_REDUCE_LEFT
        MAX_NUMBER_BRANCH: Literal[16, 256, 4096] = ScrubyConfig.MAX_NUMBER_BRANCH
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
                    data_json: bytes = leaf_path.read_bytes()
                    data: dict[str, str] = orjson.loads(data_json) or {}
                    for key, val in data.items():
                        doc = subclass.model_validate_json(val)
                        match ScrubyConfig.HASH_REDUCE_LEFT:
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
