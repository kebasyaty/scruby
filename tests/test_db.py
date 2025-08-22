"""Test Stub."""

from __future__ import annotations

import pytest
from anyio import Path

from scruby import Scruby

pytestmark = pytest.mark.asyncio(loop_scope="module")


class TestNegative:
    """Negative tests."""

    async def test_get_non_existent_key(self) -> None:
        """Get a non-existent key."""
        db = Scruby()
        with pytest.raises(KeyError):
            await db.get_key("key missing")
        await db.set_key("key name", "Some text")
        with pytest.raises(KeyError):
            await db.get_key("key missing")
        # Delete DB.
        await db.napalm()

    async def test_del_non_existent_key(self) -> None:
        """Delete a non-existent key."""
        db = Scruby()
        with pytest.raises(KeyError):
            await db.get_key("key missing")
        await db.set_key("key name", "Some text")
        with pytest.raises(KeyError):
            await db.get_key("key missing")
        # Delete DB.
        await db.napalm()

    async def test_del_non_existent_db(self) -> None:
        """Delete a non-existent database."""
        db = Scruby()
        with pytest.raises(FileNotFoundError):
            await db.napalm()


class TestPositive:
    """Positive tests."""

    async def test_create_db(self) -> None:
        """Create instance of database by default."""
        db = Scruby()
        control_path = Path(
            "ScrubyDB/a/b/6/9/2/e/6/a/3/5/e/2/6/7/2/5/a/b/5/2/0/c/4/d/0/0/0/e/a/7/d/b/leaf.json",
        )
        assert db.db_path == "ScrubyDB"
        assert await db.get_leaf_path("key name") == control_path
        # Delete DB.
        await db.napalm()

    async def test_set_key(self) -> None:
        """Testing a set_key method."""
        db = Scruby()
        assert await db.set_key("key name", "Some text") is None
        # Delete DB.
        await db.napalm()

    async def test_get_key(self) -> None:
        """Testing a get_key method."""
        db = Scruby()
        assert await db.set_key("key name", "Some text") is None
        assert await db.get_key("key name") == "Some text"
        # Delete DB.
        await db.napalm()

    async def test_has_key(self) -> None:
        """Testing a has_key method."""
        db = Scruby()
        assert await db.set_key("key name", "Some text") is None
        assert await db.has_key("key name")
        assert not await db.has_key("key missing")
        # Delete DB.
        await db.napalm()

    async def test_delete_key(self) -> None:
        """Testing a delete_key method."""
        db = Scruby()
        assert await db.set_key("key name", "Some text") is None
        assert await db.delete_key("key name") is None
        assert not await db.has_key("key name")
        # Delete DB.
        await db.napalm()
