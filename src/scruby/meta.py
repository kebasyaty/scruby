"""Metadata management."""

from __future__ import annotations

__all__ = (
    "Meta",
    "Metadata",
)

from pathlib import Path

from pydantic import BaseModel


class Meta(BaseModel):
    """Structure of metadata for collection."""

    collection_name: str
    hash_reduce_left: int
    max_number_branch: int
    counter_documents: int


class Metadata:
    """Metadata management."""

    @staticmethod
    def create(
        db_root: Path | str,
        hash_reduce_left: int,
        max_number_branch: int,
        collection_name: str,
        mode: int = 0o777,
    ) -> None:
        """Create metadata for collections."""
        meta_dir_path = Path(
            db_root,
            collection_name,
            "meta",
        )
        if not meta_dir_path.exists():
            meta_dir_path.mkdir(mode=mode, parents=True)
            meta = Meta(
                collection_name=collection_name,
                hash_reduce_left=hash_reduce_left,
                max_number_branch=max_number_branch,
                counter_documents=0,
            )
            meta_json = meta.model_dump_json()
            meta_path = Path(meta_dir_path, "meta.json")
            meta_path.write_text(meta_json, "utf-8")
