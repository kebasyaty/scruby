"""Test Stub."""

from __future__ import annotations

import datetime

import pytest
from anyio import Path
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from scruby import Scruby, constants

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: PhoneNumber


class TestNegative:
    """Negative tests."""

    async def test_get_non_existent_key(self) -> None:
        """Get a non-existent key."""
        db = Scruby(User)
        with pytest.raises(KeyError):
            await db.get_key("key missing")
        # Delete DB.
        await Scruby.napalm()

    async def test_del_non_existent_key(self) -> None:
        """Delete a non-existent key."""
        db = Scruby(User)
        with pytest.raises(KeyError):
            await db.delete_key("key missing")
        # Delete DB.
        await Scruby.napalm()

    async def test_key_not_str(self) -> None:
        """The key is not a type of `str`."""
        db = Scruby(User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        with pytest.raises(KeyError):
            await db.set_key(123, user)
        # Delete DB.
        await Scruby.napalm()

    async def test_key_is_empty(self) -> None:
        """The key should not be empty."""
        db = Scruby(User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        with pytest.raises(KeyError):
            await db.set_key("", user)
        # Delete DB.
        await Scruby.napalm()


class TestPositive:
    """Positive tests."""

    async def test_create_db(self) -> None:
        """Create instance of database by default."""
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/a/3/a/6/d/2/d/1/leaf.json",
        )
        assert await db.get_leaf_path("key name") == control_path
        # Delete DB.
        await Scruby.napalm()

    async def test_set_key(self) -> None:
        """Testing a set_key method."""
        db = Scruby(User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        assert await db.set_key("+447986123456", user) is None
        # Delete DB.
        await Scruby.napalm()

    async def test_get_key(self) -> None:
        """Testing a get_key method."""
        db = Scruby(User)
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
        await Scruby.napalm()

    async def test_has_key(self) -> None:
        """Testing a has_key method."""
        db = Scruby(User)
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
        await Scruby.napalm()

    async def test_delete_key(self) -> None:
        """Testing a delete_key method."""
        db = Scruby(User)
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
        await Scruby.napalm()

    async def test_length_separated_hash(self) -> None:
        """Length of separated hash."""
        constants.LENGTH_SEPARATED_HASH = 0  # 4294967296 keys (by default).
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/a/3/a/6/d/2/d/1/leaf.json",
        )
        assert await db.get_leaf_path("key name") == control_path
        #
        constants.LENGTH_SEPARATED_HASH = 2  # 16777216 keys.
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/a/6/d/2/d/1/leaf.json",
        )
        assert await db.get_leaf_path("key name") == control_path
        constants.LENGTH_SEPARATED_HASH = 4  # 65536 keys.
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/d/2/d/1/leaf.json",
        )
        assert await db.get_leaf_path("key name") == control_path
        #
        constants.LENGTH_SEPARATED_HASH = 6  # 256 keys (main purpose is tests).
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )
        assert await db.get_leaf_path("key name") == control_path
        #
        # Delete DB.
        await Scruby.napalm()

    async def test_find_one(self) -> None:
        """Find a single document."""
        constants.LENGTH_SEPARATED_HASH = 6  # 256 keys (main purpose is tests).
        db = Scruby(User)
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )
        await db.set_key("+447986123456", user)
        #
        # by email
        result: User | None = db.find_one(
            filter_fn=lambda doc: doc.email == "John_Smith@gmail.com",
        )
        assert result is not None
        assert result.email == user.email
        # by birthday
        result = db.find_one(
            filter_fn=lambda doc: doc.birthday == datetime.datetime(1970, 1, 1),  # noqa: DTZ001
        )
        assert result is not None
        assert result.birthday == user.birthday
        #
        # Delete DB.
        await Scruby.napalm()
