"""Methods for working with keys."""

from __future__ import annotations

__all__ = ("Keys",)

import logging
from typing import Any

import orjson

from scruby.errors import (
    KeyAlreadyExistsError,
    KeyNotExistsError,
)

logger = logging.getLogger(__name__)


class Keys:
    """Methods for working with keys."""

    async def add_key(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Asynchronous method for adding key to collection.

        Args:
            key: Key name. Type `str`.
            value: Value of key. Type, derived from `BaseModel`.

        Returns:
            None.
        """
        # Check if the Model matches the collection
        if not isinstance(value, self._class_model):
            value_class_name = value.__class__.__name__
            collection_name = self._class_model.__name__
            msg = (
                f"(add_key) Parameter `value` => Model `{value_class_name}` "
                f"does not match collection `{collection_name}`!"
            )
            logger.error(msg)
            raise TypeError(msg)
        # The path to cell of collection.
        leaf_path, prepared_key = await self._get_leaf_path(key)
        value_json: str = value.model_dump_json()
        # Write key-value to collection.
        if await leaf_path.exists():
            # Add new key.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            try:
                data[prepared_key]
            except KeyError:
                data[prepared_key] = value_json
                await leaf_path.write_bytes(orjson.dumps(data))
            else:
                err = KeyAlreadyExistsError()
                logger.error(err.message)
                raise err
        else:
            # Add new key to a blank leaf.
            await leaf_path.write_bytes(orjson.dumps({prepared_key: value_json}))
        await self._counter_documents(1)

    async def update_key(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Asynchronous method for updating key to collection.

        Args:
            key: Key name. Type `str`.
            value: Value of key. Type `BaseModel`.

        Returns:
            None.
        """
        # Check if the Model matches the collection
        if not isinstance(value, self._class_model):
            value_class_name = value.__class__.__name__
            collection_name = self._class_model.__name__
            msg = (
                f"(update_key) Parameter `value` => Model `{value_class_name}` "
                f"does not match collection `{collection_name}`!"
            )
            logger.error(msg)
            raise TypeError(msg)
        # The path to cell of collection.
        leaf_path, prepared_key = await self._get_leaf_path(key)
        value_json: str = value.model_dump_json()
        # Update the existing key.
        if await leaf_path.exists():
            # Update the existing key.
            data_json: bytes = await leaf_path.read_bytes()
            data: dict = orjson.loads(data_json) or {}
            try:
                data[prepared_key]
                data[prepared_key] = value_json
                await leaf_path.write_bytes(orjson.dumps(data))
            except KeyError:
                err = KeyNotExistsError()
                logger.error(err.message)
                raise err from None
        else:
            logger.error("The key not exists.")
            raise KeyError()

    async def get_key(self, key: str) -> Any:
        """Asynchronous method for getting value of key from collection.

        Args:
            key: Key name.

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
        logger.error(msg)
        raise KeyError()

    async def has_key(self, key: str) -> bool:
        """Asynchronous method for checking presence of key in collection.

        Args:
            key: Key name.

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
            key: Key name.

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
        logger.error(msg)
        raise KeyError()
