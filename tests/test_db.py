"""Test Stub."""

from __future__ import annotations

import pytest
from anyio import Path

from scruby import Scruby

pytestmark = pytest.mark.asyncio(loop_scope="module")


class TestNegative:
    """Negative tests."""

    async def test_stub(self) -> None:
        """Testing stub."""
        assert True


class TestPositive:
    """Positive tests."""

    async def test_create_db(self) -> None:
        """Create instance of database by default."""
        db = Scruby()
        control_path = Path("ScrubyDB/store_one/ab692e6a35e26725ab520c4d000ea7db/leaf.txt")
        assert db.db_path == "ScrubyDB"
        assert db.store_name == "store_one"
        assert await db.get_leaf_path("key name") == control_path
