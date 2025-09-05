"""Test Stub."""

from __future__ import annotations

import datetime

import pytest
from anyio import Path
from pydantic import BaseModel

from scruby import Scruby

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """Test model."""

    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: str
    phone: str


class TestNegative:
    """Negative tests."""

    async def test_get_non_existent_key(self) -> None:
        """Get a non-existent key."""
        db = Scruby(model=User)
        with pytest.raises(KeyError):
            await db.get_key("key missing")
        # Delete DB.
        await db.napalm()

    async def test_del_non_existent_key(self) -> None:
        """Delete a non-existent key."""
        db = Scruby(model=User)
        with pytest.raises(KeyError):
            await db.delete_key("key missing")
        # Delete DB.
        await db.napalm()

    async def test_del_non_existent_db(self) -> None:
        """Delete a non-existent database."""
        db = Scruby(model=User)
        with pytest.raises(FileNotFoundError):
            await db.napalm()


class TestPositive:
    """Positive tests."""

    async def test_create_db(self) -> None:
        """Create instance of database by default."""
        db = Scruby(model=User)
        control_path = Path(
            "ScrubyDB/a/b/6/9/2/e/6/a/3/5/e/2/6/7/2/5/a/b/5/2/0/c/4/d/0/0/0/e/a/7/d/b/leaf.json",
        )
        assert db.db_name == "ScrubyDB"
        assert await db.get_leaf_path("key name") == control_path
        # Delete DB.
        await db.napalm()

    async def test_set_key(self) -> None:
        """Testing a set_key method."""
        db = Scruby(model=User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        assert await db.set_key("+447986123456", user) is None
        # Delete DB.
        await db.napalm()

    async def test_get_key(self) -> None:
        """Testing a get_key method."""
        db = Scruby(model=User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        await db.set_key("+447986123456", user)
        data: User = await db.get_key("+447986123456")
        assert data.model_dump() == user.model_dump()
        # Delete DB.
        await db.napalm()

    async def test_has_key(self) -> None:
        """Testing a has_key method."""
        db = Scruby(model=User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        await db.set_key("+447986123456", user)
        assert await db.has_key("+447986123456")
        assert not await db.has_key("key missing")
        # Delete DB.
        await db.napalm()

    async def test_delete_key(self) -> None:
        """Testing a delete_key method."""
        db = Scruby(model=User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        await db.set_key("+447986123456", user)
        assert await db.delete_key("+447986123456") is None
        assert not await db.has_key("key missing")
        # Delete DB.
        await db.napalm()
