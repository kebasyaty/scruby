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
        control_path = Path(
            "ScrubyDB/store_one/a/b/6/9/2/e/6/a/3/5/e/2/6/7/2/5/a/b/5/2/0/c/4/d/0/0/0/e/a/7/d/b/leaf.txt",
        )
        assert db.db_path == "ScrubyDB"
        assert db.store_name == "store_one"
        assert await db.get_leaf_path("key name") == control_path
        # Delete DB.
        await db.napalm()
