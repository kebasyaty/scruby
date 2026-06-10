"""Cache documents to optimize work with the database."""

from __future__ import annotations

__all__ = ("DocCache",)

from typing import Any, ClassVar, Literal, Never, assert_never, final

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
        db_root: str = ScrubyConfig.db_root  # noqa: F841
        db_id: str | None = ScrubyConfig.db_id  # noqa: F841
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
        #
        branch_numbers: range = range(max_number_branch)  # noqa: F841
