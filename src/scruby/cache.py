"""Cache documents to optimize work with the database."""

from __future__ import annotations

__all__ = ("doc_cache",)

from typing import Any

# Cache documents to optimize work with the database.
# Cache structure:
# {"CollectionName": {"hash_symbol": {"hash_symbol": ...{"hash_symbol": leaf.json}}}
doc_cache: dict[str, Any] = {}
