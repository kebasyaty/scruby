"""Methods for working with collections."""

from __future__ import annotations

__all__ = ("Collection",)

from shutil import rmtree
from typing import TypeVar

from anyio import Path, to_thread

from scruby import constants

T = TypeVar("T")


class Collection[T]:
    """Methods for working with collections."""

    def collection_name(self) -> str:
        """Get collection name.

        Returns:
            Collection name.
        """
        return self._class_model.__name__

    @staticmethod
    async def collection_list() -> list[str]:
        """Get collection list."""
        target_directory = Path(constants.DB_ROOT)
        # Get all entries in the directory
        all_entries = Path.iterdir(target_directory)
        directory_names: list[str] = [entry.name async for entry in all_entries]
        return directory_names

    @staticmethod
    async def delete_collection(name: str) -> None:
        """Asynchronous method for deleting a collection by its name.

        Args:
            name (str): Collection name.

        Returns:
            None.
        """
        target_directory = f"{constants.DB_ROOT}/{name}"
        await to_thread.run_sync(rmtree, target_directory)  # pyrefly: ignore[bad-argument-type]
        return
