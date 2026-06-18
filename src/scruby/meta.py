"""Meta."""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ("Meta",)


class Meta(BaseModel):
    """Metadata of Collection."""

    collection_name: str
    hash_reduce_left: int
    max_number_branch: int
    counter_documents: int
