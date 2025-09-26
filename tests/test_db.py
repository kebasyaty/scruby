"""Test Stub."""

from __future__ import annotations

import datetime
from typing import Annotated

import pytest
from anyio import Path
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


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
        assert await db._get_leaf_path("key name") == control_path
        # Delete DB.
        await Scruby.napalm()

    async def test_metadata(self) -> None:
        """Test metadata of collection."""
        db = Scruby(User)
        meta = await db._get_meta()
        assert meta.counter_documents == 0
        meta.counter_documents = 1
        await db._set_meta(meta)
        meta_2 = await db._get_meta()
        assert meta_2.counter_documents == 1
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
        assert await db.estimated_document_count() == 0
        assert await db.set_key("+447986123456", user) is None
        assert await db.estimated_document_count() == 1
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
        assert data.phone == "+447986123456"
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
        assert await db.estimated_document_count() == 0
        await db.set_key("+447986123456", user)
        assert await db.estimated_document_count() == 1
        assert await db.delete_key("+447986123456") is None
        assert await db.estimated_document_count() == 0
        assert not await db.has_key("key missing")
        # Delete DB.
        await Scruby.napalm()

    async def test_HASH_REDUCE_LEFT(self) -> None:
        """Length of reduction hash."""
        constants.HASH_REDUCE_LEFT = 0  # 4294967296 branches in collection (by default).
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/a/3/a/6/d/2/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path
        #
        await Scruby.napalm()
        constants.HASH_REDUCE_LEFT = 2  # 16777216 branches in collection.
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/a/6/d/2/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path
        #
        await Scruby.napalm()
        constants.HASH_REDUCE_LEFT = 4  # 65536 branches in collection.
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/d/2/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path
        #
        await Scruby.napalm()
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
        db = Scruby(User)
        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path
        #
        # Delete DB.
        await Scruby.napalm()

    async def test_find_one(self) -> None:
        """Find a single document."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
        db = Scruby(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.set_key(f"+44798612345{num}", user)
        #
        # by email
        result: User | None = db.find_one(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com",
        )
        assert result is not None
        assert result.email == "John_Smith_5@gmail.com"
        # by birthday
        result_2: User | None = db.find_one(
            filter_fn=lambda doc: doc.birthday == datetime.datetime(1970, 1, 8),  # noqa: DTZ001
        )
        assert result_2 is not None
        assert result_2.birthday == datetime.datetime(1970, 1, 8)  # noqa: DTZ001
        #
        # Delete DB.
        await Scruby.napalm()

    async def test_find_many(self) -> None:
        """Find documents."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
        db = Scruby(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.set_key(f"+44798612345{num}", user)
        #
        # by emails
        results: list[User] | None = db.find_many(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert results is not None
        assert len(results) == 2
        assert results[0].email in ["John_Smith_5@gmail.com", "John_Smith_8@gmail.com"]
        assert results[1].email in ["John_Smith_5@gmail.com", "John_Smith_8@gmail.com"]
        #
        # Delete DB.
        await Scruby.napalm()

    async def test_collection_name(self) -> None:
        """Test a collection_name method."""
        constants.HASH_REDUCE_LEFT = 0  # 4294967296 branches in collection (by default).
        db = Scruby(User)
        assert db.collection_name() == "User"
        # Delete DB.
        await Scruby.napalm()

    async def test_collection_full_name(self) -> None:
        """Test a collection_full_name method."""
        constants.HASH_REDUCE_LEFT = 0  # 4294967296 branches in collection (by default).
        db = Scruby(User)
        assert db.collection_full_name() == "ScrubyDB/User"
        # Delete DB.
        await Scruby.napalm()

    async def test_count_documents(self) -> None:
        """Test a count_documents method."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
        db = Scruby(User)
        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.set_key(f"+44798612345{num}", user)
        assert await db.estimated_document_count() == 9
        result: int = db.count_documents(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert result == 2
        #
        # Delete DB.
        await Scruby.napalm()

    async def test_find_many_and_delete(self) -> None:
        """Test a find_many_and_delete method."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
        db = Scruby(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.set_key(f"+44798612345{num}", user)
        #
        # by emails
        result: int = db.find_many_and_delete(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert result == 2
        assert await db.estimated_document_count() == 7
        #
        # Delete DB.
        await Scruby.napalm()
