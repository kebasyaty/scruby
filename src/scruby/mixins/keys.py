# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Methods for working with keys."""

from __future__ import annotations

__all__ = ("Keys",)


import re
import zlib
from datetime import datetime
from typing import Any, Never, assert_never, final
from zoneinfo import ZoneInfo

import orjson

from scruby.cache import DocCache
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
                f"(add_doc) Parameter `doc` => Model `{doc_class_name}` does not match collection `{collection_name}`!"
            )
            raise TypeError(msg)
        # Get the path to the collection cell.
        leaf_path, prepared_key, key_as_hash = await self._get_leaf_path(doc.key)
        # Init a `created_at` and `updated_at` fields
        tz = ZoneInfo("UTC")
        doc.created_at = datetime.now(tz)
        doc.updated_at = datetime.now(tz)
        # Convert doc to json
        doc_json: str = doc.model_dump_json()
        # Check if a collection cell exists.
        if await leaf_path.exists():
            # Get a document from the database.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            # Check to see if the document key is missing.
            if data.get(prepared_key) is None:
                # Add a new document to the database.
                data[prepared_key] = doc_json
                await leaf_path.write_bytes(orjson.dumps(data))
            else:
                raise KeyAlreadyExistsError()
        else:
            # Add new document to a blank leaf.
            await leaf_path.write_bytes(orjson.dumps({prepared_key: doc_json}))
        # Update document counter
        await self._counter_documents(1)
        # Add new document to cache
        collection_name = self._class_model.__name__
        match self._hash_reduce_left:
            case 7:
                DocCache.cache[collection_name][key_as_hash[0]][prepared_key] = doc
            case 6:
                DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][prepared_key] = doc
            case 5:
                DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][key_as_hash[2]][prepared_key] = doc
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @final
    async def update_doc(self, doc: Any) -> None:
        """Asynchronous method for updating document to collection.

        Args:
            doc (Any): Value of key. Type `ScrubyModel`.

        Returns:
            None.
        """
        # Check if the Model matches the collection.
        if not isinstance(doc, self._class_model):
            doc_class_name = doc.__class__.__name__
            collection_name = self._class_model.__name__
            msg = (
                f"(update_doc) Parameter `doc` => Model `{doc_class_name}` "
                f"does not match collection `{collection_name}`!"
            )
            raise TypeError(msg)
        # Get the path to the collection cell.
        leaf_path, prepared_key, key_as_hash = await self._get_leaf_path(doc.key)
        # Update a `updated_at` field.
        doc.updated_at = datetime.now(ZoneInfo("UTC"))
        # Convert doc to json.
        doc_json: str = doc.model_dump_json()
        # Check if a collection cell exists.
        if await leaf_path.exists():
            # Get a document from the database.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            # Check if the document key exists.
            if data.get(prepared_key) is not None:
                # Update a document from database.
                data[prepared_key] = doc_json
                await leaf_path.write_bytes(orjson.dumps(data))
                # Update a document from cache.
                collection_name = self._class_model.__name__
                match self._hash_reduce_left:
                    case 7:
                        DocCache.cache[collection_name][key_as_hash[0]][prepared_key] = doc
                    case 6:
                        DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][prepared_key] = doc
                    case 5:
                        DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][key_as_hash[2]][
                            prepared_key
                        ] = doc
                    case _ as unreachable:
                        assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]
            else:
                raise KeyNotExistsError()
        else:
            msg: str = f"`update_doc` - The key `{doc.key}` is missing!"
            raise KeyError(msg)

    @final
    def get_doc(self, key: str) -> Any | None:
        """Asynchronous method for getting document from collection the by key.

        Args:
            key (str): Key name.

        Returns:
            Value of key or KeyError.
        """
        if not isinstance(key, str):
            raise KeyError("The key is not a string.")
        # Prepare key.
        # Removes spaces at the beginning and end of a string.
        # Replaces all whitespace characters with a single space.
        prepared_key = re.sub(r"\s+", " ", key).strip().lower()
        # Check the key for an empty string.
        if len(prepared_key) == 0:
            raise KeyError("The key should not be empty.")
        # Key to crc32 sum.
        key_as_hash: str = f"{zlib.crc32(prepared_key.encode('utf-8')):08x}"[self._hash_reduce_left :]
        # Get value of key from cache
        collection_name = self._class_model.__name__
        match self._hash_reduce_left:
            case 7:
                return DocCache.cache[collection_name][key_as_hash[0]].get(prepared_key)
            case 6:
                return DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]].get(prepared_key)
            case 5:
                return DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][key_as_hash[2]].get(prepared_key)
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]

    @final
    def has_key(self, key: str) -> bool:
        """Asynchronous method for checking presence of key in collection.

        Args:
            key (str): Key name.

        Returns:
            True, if the key is present.
        """
        if not isinstance(key, str):
            raise KeyError("The key is not a string.")
        # Prepare key.
        # Removes spaces at the beginning and end of a string.
        # Replaces all whitespace characters with a single space.
        prepared_key = re.sub(r"\s+", " ", key).strip().lower()
        # Check the key for an empty string.
        if len(prepared_key) == 0:
            raise KeyError("The key should not be empty.")
        # Key to crc32 sum.
        key_as_hash: str = f"{zlib.crc32(prepared_key.encode('utf-8')):08x}"[self._hash_reduce_left :]
        # Get value of key from cache
        collection_name = self._class_model.__name__
        is_exists: bool = False
        match self._hash_reduce_left:
            case 7:
                is_exists = DocCache.cache[collection_name][key_as_hash[0]].get(prepared_key) is not None
            case 6:
                is_exists = (
                    DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]].get(prepared_key) is not None
                )
            case 5:
                is_exists = (
                    DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][key_as_hash[2]].get(prepared_key)
                    is not None
                )
            case _ as unreachable:
                assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]
        return is_exists

    @final
    async def delete_doc(self, key: str) -> None:
        """Asynchronous method for deleting document from collection the by key.

        Args:
            key (str): Key name.

        Returns:
            None.
        """
        # The path to the database cell.
        leaf_path, prepared_key, key_as_hash = await self._get_leaf_path(key)
        # Deleting key.
        if await leaf_path.exists():
            # Delete a document from the file system
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            if data.get(prepared_key) is not None:
                # Delete a document from database
                del data[prepared_key]
                await leaf_path.write_bytes(orjson.dumps(data))
                await self._counter_documents(-1)
                # Delete a document from cache
                collection_name = self._class_model.__name__
                match self._hash_reduce_left:
                    case 7:
                        del DocCache.cache[collection_name][key_as_hash[0]][prepared_key]
                    case 6:
                        del DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][prepared_key]
                    case 5:
                        del DocCache.cache[collection_name][key_as_hash[0]][key_as_hash[1]][key_as_hash[2]][
                            prepared_key
                        ]
                    case _ as unreachable:
                        assert_never(Never(unreachable))  # pyrefly: ignore[not-callable]
            else:
                raise KeyNotExistsError()
        else:
            msg: str = f"`delete_doc` - The key `{key}` is missing!"
            raise KeyError(msg)
