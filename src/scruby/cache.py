"""Cache documents to optimize work with the database."""

from __future__ import annotations

__all__ = ("DocCache",)

from typing import Any, ClassVar, final


@final
class DocCache:
    """Cache documents to optimize work with the database."""

    # Cache structure:
    # {"CollectionName": {"hash_symbol": {"hash_symbol": ...{"hash_symbol": leaf.json}}}
    cache: ClassVar[dict[str, Any]] = {}
