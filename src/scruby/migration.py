"""Migration."""

from __future__ import annotations

__all__ = ("Migration",)

from pathlib import Path
from shutil import rmtree
from typing import Any

from scruby.utils import Utils


class Migration:
    """Migration."""

    @classmethod
    def run(cls, db_root: Path | str, subclasses: list[Any]) -> None:
        """Run migration."""
        # Delete collections whose models have been deleted
        cls.delete_orphan_collections(db_root, subclasses)

    @staticmethod
    def delete_orphan_collections(db_root: Path | str, subclasses: list[Any]) -> None:
        """Delete collections whose models have been deleted."""
        model_collection_list: list[str] = [subclass.__name__ for subclass in subclasses]
        db_collection_list: list[str] | None = Utils.db_collection_list(db_root)

        if db_collection_list is not None:
            for collection_name in db_collection_list:
                if collection_name not in model_collection_list:
                    target_directory = Path(db_root, collection_name)
                    rmtree(target_directory)
