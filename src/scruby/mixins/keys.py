# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for working with keys."""

from __future__ import annotations

__all__ = ("Keys",)


from datetime import datetime
from typing import Any, final
from zoneinfo import ZoneInfo

import aiodbm

from scruby.errors import (
    KeyAlreadyExistsError,
    KeyNotExistsError,
)


class Keys:
    """Methods for working with keys."""

    @final
    async def add_doc(self, doc: Any) -> None:
        """Asynchronous method for adding document to collection.

        Args:
            doc (Any): Value of key. Type, derived from `ScrubyModel`.

        Returns:
            None.
        """
        # Check if the Model matches the collection
        if not isinstance(doc, self._class_model):
            doc_class_name = doc.__class__.__name__
            collection_name = self._class_model.__name__
            msg = (
                "Method: `add_doc` > Parameter: `doc` => "
                + f"Model `{doc_class_name}` does not match collection `{collection_name}`!"
            )
            raise TypeError(msg)

        # If a password field is present, it must not be empty
        if "password" in self.model_fields and not bool(doc.password):
            msg = "Method: `add_doc` => The `password` field is empty"
            raise ValueError(msg)

        # Get the path to the collection cell
        leaf_path, prepared_key = await self._get_leaf_path(doc.key)
        # Init a `created_at` and `updated_at` fields
        tz = ZoneInfo("UTC")
        doc.created_at = datetime.now(tz)
        doc.updated_at = datetime.now(tz)
        # Convert doc to json
        doc_json: str = doc.model_dump_json()

        async with aiodbm.open(str(leaf_path), flag="c", mode=self._mode) as leaf_db:
            # Raise an exception if the key is exists
            if await leaf_db.exists(prepared_key):
                raise KeyAlreadyExistsError()
            # Add a new document to the database
            await leaf_db.set(prepared_key, doc_json)
        # Update document counter
        await self._counter_documents(1)

    @final
    async def update_doc(self, doc: Any) -> None:
        """Asynchronous method for updating document to collection.

        Args:
            doc (Any): Value of key. Type `ScrubyModel`.

        Returns:
            None.
        """
        # Check if the Model matches the collection
        if not isinstance(doc, self._class_model):
            doc_class_name = doc.__class__.__name__
            collection_name = self._class_model.__name__
            msg = (
                f"Method: `update_doc` > Parameter: `doc` => Model `{doc_class_name}` "
                f"does not match collection `{collection_name}`!"
            )
            raise TypeError(msg)

        # If a password field is present, it must not be empty
        if "password" in self.model_fields and not bool(doc.password):
            msg = "Method: `update_doc` => The `password` field is empty"
            raise ValueError(msg)

        # Get the path to the collection cell
        leaf_path, prepared_key = await self._get_leaf_path(doc.key)
        # Update a `updated_at` field
        doc.updated_at = datetime.now(ZoneInfo("UTC"))
        # Convert doc to json.
        doc_json: str = doc.model_dump_json()

        async with aiodbm.open(str(leaf_path), flag="c", mode=self._mode) as leaf_db:
            # Raise an exception if the key is missing
            if not await leaf_db.exists(prepared_key):
                raise KeyNotExistsError()
            # Update document to the database
            await leaf_db.set(prepared_key, doc_json)

    @final
    async def get_doc(self, key: str) -> Any | None:
        """Asynchronous method for getting document from collection the by key.

        Args:
            key (str): Key name.

        Returns:
            Value of key or KeyError.
        """
        if not isinstance(key, str):
            raise KeyError("The key is not a string.")

        # Get the path to the collection cell
        leaf_path, prepared_key = await self._get_leaf_path(key)

        async with aiodbm.open(str(leaf_path), flag="c", mode=self._mode) as leaf_db:
            # If the key is missing, return None
            if not await leaf_db.exists(prepared_key):
                return None

            doc_json = await leaf_db.get(prepared_key)
            return self._class_model.model_validate_json(doc_json)

    @final
    async def has_key(self, key: str) -> bool:
        """Asynchronous method for checking presence of key in collection.

        Args:
            key (str): Key name.

        Returns:
            True, if the key is present.
        """
        # Get path to cell of collection.
        leaf_path, prepared_key = await self._get_leaf_path(key)

        async with aiodbm.open(str(leaf_path), flag="c", mode=self._mode) as leaf_db:
            return await leaf_db.exists(prepared_key)

    @final
    async def delete_doc(self, key: str) -> None:
        """Asynchronous method for deleting document from collection the by key.

        Args:
            key (str): Key name.

        Returns:
            None.
        """
        # The path to the database cell.
        leaf_path, prepared_key = await self._get_leaf_path(key)

        # Deleting key.
        async with aiodbm.open(str(leaf_path), flag="c", mode=self._mode) as leaf_db:
            # Raise an exception if the key is missing
            if not await leaf_db.exists(prepared_key):
                raise KeyNotExistsError()

            await leaf_db.delete(prepared_key)
            await self._counter_documents(-1)
