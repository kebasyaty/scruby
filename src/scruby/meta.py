"""Meta.

Metadata management.
"""

from __future__ import annotations

__all__ = (
    "Meta",
    "Metadata",
)

from pathlib import Path

from pydantic import BaseModel

from scruby.config import ScrubyConfig


class Meta(BaseModel):
    """Structure of metadata for collection."""

    collection_name: str
    hash_reduce_left: int
    max_number_branch: int
    counter_documents: int


class Metadata:
    """Metadata management."""

    @staticmethod
    def create(collection_name: str) -> None:
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
            meta = Meta(
                collection_name=collection_name,
                hash_reduce_left=ScrubyConfig.HASH_REDUCE_LEFT,
                max_number_branch=ScrubyConfig.MAX_NUMBER_BRANCH,
                counter_documents=0,
            )
            meta_json = meta.model_dump_json()
            meta_path = Path(meta_dir_path, "meta.json")
            meta_path.write_text(meta_json, "utf-8")
