"""Cache documents to optimize work with the database."""

from __future__ import annotations

__all__ = ("DocCache",)

from pathlib import Path
from typing import Any, ClassVar, Literal, Never, assert_never, final

import orjson

from scruby.config import ScrubyConfig


@final
class DocCache:
    """Cache documents to optimize work with the database."""

    # Cache structure:
    # {"CollectionName": {"hash_symbol": {"hash_symbol": ...{"hash_symbol": leaf.json}}}
    cache: ClassVar[dict[str, Any]] = {}

    @classmethod
    def load_cache(cls) -> None:
        """Load all documents from the database into the cache."""
        db_root: Path = Path(ScrubyConfig.db_root)
        HASH_REDUCE_LEFT: Literal[4, 6] = ScrubyConfig.HASH_REDUCE_LEFT
        max_number_branch: int = 0

        # Get maximum number of branches.
        match HASH_REDUCE_LEFT:
            case 4:
                max_number_branch = 65536
            case 6:
                max_number_branch = 256
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

        branch_numbers: range = range(max_number_branch)
        # Leave function if database does not exist
        if not db_root.exists():
            return
        # Get a list of collection names
        collections = [item.name for item in db_root.iterdir() if item.is_dir()]

        for collection_name in collections:
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

                separated_hash = branch_number_as_hash.split()
                match HASH_REDUCE_LEFT:
                    case 6:
                        cls.cache[collection_name] = {separated_hash[0]: {separated_hash[1]: {}}}
                    case 4:
                        cls.cache[collection_name] = {
                            separated_hash[0]: {separated_hash[1]: {separated_hash[2]: {separated_hash[3]: {}}}},
                        }

                if leaf_path.exists():
                    data_json: bytes = leaf_path.read_bytes()
                    data: dict[str, str] = orjson.loads(data_json) or {}
                    for key, val in data.items():
                        doc = orjson.loads(val)
                        match HASH_REDUCE_LEFT:
                            case 6:
                                cls.cache[collection_name][separated_hash[0]][separated_hash[1]][key] = doc
                            case 4:
                                cls.cache[collection_name][separated_hash[0]][separated_hash[1]][separated_hash[2]][
                                    separated_hash[3]
                                ][key] = doc
