"""Test Stub."""

from __future__ import annotations

import pytest

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
        assert db.db_path == "ScrubyDB"
        assert db.store_name == "store_one"
