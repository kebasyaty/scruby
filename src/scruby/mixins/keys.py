# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
#
"""Methods for working with keys."""

from __future__ import annotations

__all__ = ("Keys",)

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import orjson

from scruby.errors import (
    KeyAlreadyExistsError,
    KeyNotExistsError,
)


class Keys:
    """Methods for working with keys."""

    async def add_doc(self, doc: Any) -> None:
        """Asynchronous method for adding document to collection.

        Args:
            doc (Any): Value of key. Type, derived from `BaseModel`.

        Returns:
            None.
        """
        # Check if the Model matches the collection
        if not isinstance(doc, self._class_model):
            doc_class_name = doc.__class__.__name__
            collection_name = self._class_model.__name__
            msg = (
                f"(add_doc) Parameter `doc` => Model `{doc_class_name}` does not match collection `{collection_name}`!"
            )
            logging.error(msg)
            raise TypeError(msg)
        # The path to cell of collection.
        leaf_path, prepared_key = await self._get_leaf_path(doc.key)
        # Init a `created_at` and `updated_at` fields
        tz = ZoneInfo("UTC")
        doc.created_at = datetime.now(tz)
        doc.updated_at = datetime.now(tz)
        # Convert doc to json
        doc_json: str = doc.model_dump_json()
        # Write key-value to collection.
        if await leaf_path.exists():
            # Add new key.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            try:
                data[prepared_key]
            except KeyError:
                data[prepared_key] = doc_json
                await leaf_path.write_bytes(orjson.dumps(data))
            else:
                err = KeyAlreadyExistsError()
                logging.error(err.message)
                raise err
        else:
            # Add new document to a blank leaf.
            await leaf_path.write_bytes(orjson.dumps({prepared_key: doc_json}))
        await self._counter_documents(1)

    async def update_doc(self, doc: Any) -> None:
        """Asynchronous method for updating key to collection.

        Args:
            doc (Any): Value of key. Type `BaseModel`.

        Returns:
            None.
        """
        # Check if the Model matches the collection
        if not isinstance(doc, self._class_model):
            doc_class_name = doc.__class__.__name__
            collection_name = self._class_model.__name__
            msg = (
                f"(update_doc) Parameter `doc` => Model `{doc_class_name}` "
                f"does not match collection `{collection_name}`!"
            )
            logging.error(msg)
            raise TypeError(msg)
        # The path to cell of collection.
        leaf_path, prepared_key = await self._get_leaf_path(doc.key)
        # Update a `updated_at` field
        doc.updated_at = datetime.now(ZoneInfo("UTC"))
        # Convert doc to json
        doc_json: str = doc.model_dump_json()
        # Update the existing key.
        if await leaf_path.exists():
            # Update the existing key.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            try:
                data[prepared_key]
                data[prepared_key] = doc_json
                await leaf_path.write_bytes(orjson.dumps(data))
            except KeyError:
                err = KeyNotExistsError()
                logging.error(err.message)
                raise err from None
        else:
            logging.error("The key not exists.")
            raise KeyError()

    async def get_key(self, key: str) -> Any:
        """Asynchronous method for getting value of key from collection.

        Args:
            key (str): Key name.

        Returns:
            Value of key or KeyError.
        """
        # The path to the database cell.
        leaf_path, prepared_key = await self._get_leaf_path(key)
        # Get value of key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            obj: Any = self._class_model.model_validate_json(data[prepared_key])
            return obj
        msg: str = "`get_key` - The unacceptable key value."
        logging.error(msg)
        raise KeyError()

    async def has_key(self, key: str) -> bool:
        """Asynchronous method for checking presence of key in collection.

        Args:
            key (str): Key name.

        Returns:
            True, if the key is present.
        """
        # Get path to cell of collection.
        leaf_path, prepared_key = await self._get_leaf_path(key)
        # Checking whether there is a key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            try:
                data[prepared_key]
                return True
            except KeyError:
                return False
        return False

    async def delete_key(self, key: str) -> None:
        """Asynchronous method for deleting key from collection.

        Args:
            key (str): Key name.

        Returns:
            None.
        """
        # The path to the database cell.
        leaf_path, prepared_key = await self._get_leaf_path(key)
        # Deleting key.
        if await leaf_path.exists():
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            del data[prepared_key]
            await leaf_path.write_bytes(orjson.dumps(data))
            await self._counter_documents(-1)
            return
        msg: str = "`delete_key` - The unacceptable key value."
        logging.error(msg)
        raise KeyError()
