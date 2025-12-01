"""Test Database."""

from __future__ import annotations

import concurrent.futures
import datetime
from collections.abc import Callable
from typing import Annotated, Any

import pytest
from anyio import Path
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.errors import (
    KeyAlreadyExistsError,
    KeyNotExistsError,
)

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


class User2(BaseModel):
    """User model."""

    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


async def custom_task(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    limit_docs: int,  # noqa: ARG001
) -> Any:
    """Custom task.

    Calculate the number of users named John.
    """
    max_workers: int | None = None
    counter: int = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        for branch_number in branch_numbers:
            future = executor.submit(
                get_docs_fn,
                branch_number,
                hash_reduce_left,
                db_root,
                class_model,
            )
            docs = await future.result()
            for doc in docs:
                if doc.first_name == "John":
                    counter += 1
    return counter


class TestNegative:
    """Negative tests."""

    async def test_typeerror_class_model(self) -> None:
        """`class_model` does not contain the base class `pydantic.BaseMode."""
        with pytest.raises(
            TypeError,
            match=r"`class_model` does not contain the base class `pydantic.BaseModel`!",
        ):
            await Scruby.create(dict)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_get_non_existent_key(self) -> None:
        """Get a non-existent key."""
        db = await Scruby.create(User)

        with pytest.raises(KeyError):
            await db.get_key("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_del_non_existent_key(self) -> None:
        """Delete a non-existent key."""
        db = await Scruby.create(User)

        with pytest.raises(KeyError):
            await db.delete_key("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_not_str(self) -> None:
        """The key is not a type of `str`."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        with pytest.raises(KeyError):
            await db.add_key(123, user)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_is_empty(self) -> None:
        """The key should not be empty."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        with pytest.raises(KeyError):
            await db.add_key("", user)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_already_exists(self) -> None:
        """If the key already exists."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        await db.add_key(user.phone, user)

        with pytest.raises(KeyAlreadyExistsError):
            await db.add_key(user.phone, user)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_not_exists(self) -> None:
        """If the key not exists."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        with pytest.raises(KeyError):
            await db.update_key(user.phone, user)

        await db.add_key(user.phone, user)
        await db.delete_key(user.phone)

        with pytest.raises(KeyNotExistsError):
            await db.update_key(user.phone, user)
        #
        # Delete DB.
        Scruby.napalm()


class TestPositive:
    """Positive tests."""

    async def test_create_db(self) -> None:
        """Create instance of database by default."""
        db = await Scruby.create(User)

        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )

        assert await db._get_leaf_path("key name") == control_path
        #
        # Delete DB.
        Scruby.napalm()

    async def test_collection_list(self) -> None:
        """Testing a `collection_list` methopd."""
        await Scruby.create(User)

        collection_list = await Scruby.collection_list()
        assert "User" in collection_list

        await Scruby.create(User2)

        collection_list = await Scruby.collection_list()
        assert "User" in collection_list
        assert "User2" in collection_list
        #
        # Delete DB.
        Scruby.napalm()

    async def test_delete_collection(self) -> None:
        """Testing a `delete_collection` methopd."""
        await Scruby.create(User)
        await Scruby.create(User2)

        collection_list = await Scruby.collection_list()
        assert "User" in collection_list
        assert "User2" in collection_list

        await Scruby.delete_collection("User")

        collection_list = await Scruby.collection_list()
        assert "User2" in collection_list

        await Scruby.delete_collection("User2")

        collection_list = await Scruby.collection_list()
        assert len(collection_list) == 0
        #
        # Delete DB.
        Scruby.napalm()

    async def test_metadata(self) -> None:
        """Test metadata of collection."""
        db = await Scruby.create(User)

        meta = await db.get_meta()
        assert meta.counter_documents == 0
        meta.counter_documents = 1
        await db._set_meta(meta)
        meta_2 = await db.get_meta()
        assert meta_2.counter_documents == 1
        #
        # Delete DB.
        Scruby.napalm()

    async def test_add_key(self) -> None:
        """Testing a add_key method."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        assert await db.estimated_document_count() == 0
        assert await db.add_key(user.phone, user) is None
        assert await db.estimated_document_count() == 1
        #
        # Delete DB.
        Scruby.napalm()

    async def test_update_key(self) -> None:
        """Testing a update_key method."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        assert await db.estimated_document_count() == 0
        await db.add_key(user.phone, user)
        assert await db.estimated_document_count() == 1
        await db.update_key(user.phone, user)
        assert await db.estimated_document_count() == 1
        #
        # Delete DB.
        Scruby.napalm()

    async def test_get_key(self) -> None:
        """Testing a get_key method."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        await db.add_key(user.phone, user)
        data: User = await db.get_key("+447986123456")
        assert data.model_dump() == user.model_dump()
        assert data.phone == "+447986123456"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_has_key(self) -> None:
        """Testing a has_key method."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        await db.add_key(user.phone, user)
        assert await db.has_key("+447986123456")
        assert not await db.has_key("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_delete_key(self) -> None:
        """Testing a delete_key method."""
        db = await Scruby.create(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        assert await db.estimated_document_count() == 0
        await db.add_key(user.phone, user)
        assert await db.estimated_document_count() == 1
        assert await db.delete_key("+447986123456") is None
        assert await db.estimated_document_count() == 0
        assert not await db.has_key("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_HASH_REDUCE_LEFT(self) -> None:
        """Length of reduction hash."""
        db = await Scruby.create(User)
        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path

        Scruby.napalm()
        constants.HASH_REDUCE_LEFT = 2  # 16777216 branches in collection.
        db = await Scruby.create(User)
        control_path = Path(
            "ScrubyDB/User/a/6/d/2/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path

        Scruby.napalm()
        constants.HASH_REDUCE_LEFT = 4  # 65536 branches in collection.
        db = await Scruby.create(User)
        control_path = Path(
            "ScrubyDB/User/d/2/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path

        Scruby.napalm()
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
        db = await Scruby.create(User)
        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )
        assert await db._get_leaf_path("key name") == control_path
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_one(self) -> None:
        """Find a single document."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).

        db = await Scruby.create(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.add_key(user.phone, user)

        # by email
        result: User | None = await db.find_one(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com",
        )
        assert result is not None
        assert result.email == "John_Smith_5@gmail.com"

        # by birthday
        result_2: User | None = await db.find_one(
            filter_fn=lambda doc: doc.birthday == datetime.datetime(1970, 1, 8),  # noqa: DTZ001
        )
        assert result_2 is not None
        assert result_2.birthday == datetime.datetime(1970, 1, 8)  # noqa: DTZ001
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_many(self) -> None:
        """Find documents."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).

        db = await Scruby.create(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.add_key(user.phone, user)

        # by emails
        results: list[User] | None = await db.find_many(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert results is not None
        assert len(results) == 2
        assert results[0].email in ["John_Smith_5@gmail.com", "John_Smith_8@gmail.com"]
        assert results[1].email in ["John_Smith_5@gmail.com", "John_Smith_8@gmail.com"]
        #
        # Delete DB.
        Scruby.napalm()

    async def test_collection_name(self) -> None:
        """Test a collection_name method."""
        db = await Scruby.create(User)

        assert db.collection_name() == "User"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_count_documents(self) -> None:
        """Test a count_documents method."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).

        db = await Scruby.create(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.add_key(user.phone, user)

        assert await db.estimated_document_count() == 9
        result: int = await db.count_documents(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert result == 2
        #
        # Delete DB.
        Scruby.napalm()

    async def test_delete_many(self) -> None:
        """Test a delete_many method."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).

        db = await Scruby.create(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.add_key(user.phone, user)

        # by emails
        result: int = await db.delete_many(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert result == 2
        assert await db.estimated_document_count() == 7
        result = await db.count_documents(
            filter_fn=lambda _: True,
        )
        assert result == 7
        #
        # Delete DB.
        Scruby.napalm()

    async def test_run_custom_task(self) -> None:
        """Test a run_custom_task method."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).

        db = await Scruby.create(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.add_key(user.phone, user)

        result = await db.run_custom_task(custom_task)
        assert result == 9
        #
        # Delete DB.
        Scruby.napalm()

    async def test_update_many(self) -> None:
        """Test a update_many method."""
        constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).

        db = await Scruby.create(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime.datetime(1970, 1, num),  # noqa: DTZ001
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await db.add_key(user.phone, user)

        number_updated_users = await db.update_many(
            filter_fn=lambda _: True,  # Update all documents
            new_data={"first_name": "Georg"},
        )
        assert number_updated_users == 9
        #
        # by email
        users: list[User] | None = await db.find_many(
            filter_fn=lambda _: True,  # Find all documents
        )
        assert users is not None
        for user in users:
            assert user.first_name == "Georg"
        #
        # Delete DB.
        Scruby.napalm()
