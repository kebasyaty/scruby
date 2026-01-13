"""Test Database."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

import pytest
from anyio import Path
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, settings
from scruby.errors import (
    KeyAlreadyExistsError,
    KeyNotExistsError,
)

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(ScrubyModel):
    """User model."""

    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


class User2(ScrubyModel):
    """User model."""

    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


class User3(ScrubyModel):
    """User model."""

    username: str = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["username"],
    )


class User4(BaseModel):
    """Invalid model type."""

    username: str = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["username"],
    )


class User5(ScrubyModel):
    """Key of Model is missing."""

    username: str = Field(strict=True)


def custom_task(
    search_task_fn: Callable,
    filter_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None = None,
) -> Any:
    """Custom task.

    Calculate the number of users named John.
    """
    counter: int = 0
    # Run quantum loop
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        for branch_number in branch_numbers:
            future = executor.submit(
                search_task_fn,
                branch_number,
                filter_fn,
                hash_reduce_left,
                db_root,
                class_model,
            )
            docs = future.result()
            if docs is not None:
                for _ in docs:
                    counter += 1
    return counter


class TestNegative:
    """Negative tests."""

    async def test_invalid_model_type(self) -> None:
        """Invalid model type."""
        with pytest.raises(
            AssertionError,
            match=r"Method: `collection` => argument `class_model` does not contain the base class `ScrubyModel`!",
        ):
            await Scruby.collection(User4)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_model_key_is_missing(self) -> None:
        """Key of Model is missing."""
        with pytest.raises(
            AssertionError,
            match=r"Model: User5 => The `key` field is missing!",
        ):
            await Scruby.collection(User5)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_add_doc_value_does_not_match_collection(self) -> None:
        """add_doc() - Parameter `value` does not match current collection."""
        user2 = User2(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        user_coll = await Scruby.collection(User)

        with pytest.raises(
            TypeError,
            match=r"\(add_doc\) Parameter `doc` => Model `User2` does not match collection `User`!",
        ):
            await user_coll.add_doc(user2)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_update_doc_value_does_not_match_collection(self) -> None:
        """update_doc() - Parameter `value` does not match current collection."""
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        user2 = User2(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        user_coll = await Scruby.collection(User)
        await user_coll.add_doc(user)

        with pytest.raises(
            TypeError,
            match=r"\(update_doc\) Parameter `doc` => Model `User2` does not match collection `User`!",
        ):
            await user_coll.update_doc(user2)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_get_non_existent_key(self) -> None:
        """Get a non-existent key."""
        user_coll = await Scruby.collection(User)

        with pytest.raises(KeyError):
            await user_coll.get_doc("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_del_non_existent_key(self) -> None:
        """Delete a non-existent key."""
        user_coll = await Scruby.collection(User)

        with pytest.raises(KeyError):
            await user_coll.delete_doc("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_is_empty(self) -> None:
        """The key should not be empty."""
        user_coll = await Scruby.collection(User3)

        user = User3(username="")
        with pytest.raises(KeyError, match=r"The key should not be empty."):
            await user_coll.add_doc(user)

        user = User3(username=" ")
        with pytest.raises(KeyError, match=r"The key should not be empty."):
            await user_coll.add_doc(user)

        user = User3(username="  ")
        with pytest.raises(KeyError, match=r"The key should not be empty."):
            await user_coll.add_doc(user)

        user = User3(username="\t\n\r\f\v")
        with pytest.raises(KeyError, match=r"The key should not be empty."):
            await user_coll.add_doc(user)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_already_exists(self) -> None:
        """If the key already exists."""
        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        await user_coll.add_doc(user)

        with pytest.raises(KeyAlreadyExistsError):
            await user_coll.add_doc(user)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_not_exists(self) -> None:
        """If the key not exists."""
        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        with pytest.raises(KeyError):
            await user_coll.update_doc(user)

        await user_coll.add_doc(user)
        await user_coll.delete_doc(user.key)

        with pytest.raises(KeyNotExistsError):
            await user_coll.update_doc(user)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_many_page_number_less_than_one(self) -> None:
        """The `page_number` parameter must not be less than one."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await user_coll.add_doc(user)

        # limit docs = 5, page number = 0
        with pytest.raises(
            AssertionError,
            match=r"`find_many` => The `page_number` parameter must not be less than one.",
        ):
            await user_coll.find_many(
                filter_fn=lambda doc: doc.last_name == "Smith",
                limit_docs=5,
                page_number=0,
            )

        # limit docs = 5, page number = -1
        with pytest.raises(
            AssertionError,
            match=r"`find_many` => The `page_number` parameter must not be less than one.",
        ):
            await user_coll.find_many(
                filter_fn=lambda doc: doc.last_name == "Smith",
                limit_docs=5,
                page_number=-1,
            )
        #
        # Delete DB.
        Scruby.napalm()


class TestPositive:
    """Positive tests."""

    async def test_create_db(self) -> None:
        """Create instance of database by default."""
        user_coll = await Scruby.collection(User)

        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )

        key_name = "key name"

        leaf_path, prepared_key = await user_coll._get_leaf_path(key_name)

        assert leaf_path == control_path
        assert prepared_key == key_name
        #
        # Delete DB.
        Scruby.napalm()

    async def test_collection_list(self) -> None:
        """Testing a `collection_list` methopd."""
        await Scruby.collection(User)

        collection_list = await Scruby.collection_list()
        assert "User" in collection_list

        await Scruby.collection(User2)

        collection_list = await Scruby.collection_list()
        assert "User" in collection_list
        assert "User2" in collection_list
        #
        # Delete DB.
        Scruby.napalm()

    async def test_delete_collection(self) -> None:
        """Testing a `delete_collection` methopd."""
        await Scruby.collection(User)
        await Scruby.collection(User2)

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
        user_coll = await Scruby.collection(User)

        meta = await user_coll.get_meta()
        assert meta.db_root == "ScrubyDB"
        assert meta.collection_name == "User"
        assert meta.hash_reduce_left == 6
        assert meta.max_branch_number == 256
        assert meta.counter_documents == 0

        meta.counter_documents = 1
        await user_coll._set_meta(meta)

        meta_2 = await user_coll.get_meta()
        assert meta_2.db_root == "ScrubyDB"
        assert meta_2.collection_name == "User"
        assert meta_2.hash_reduce_left == 6
        assert meta_2.max_branch_number == 256
        assert meta_2.counter_documents == 1
        #
        # Delete DB.
        Scruby.napalm()

    async def test_add_doc(self) -> None:
        """Testing a add_doc method."""
        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        assert await user_coll.estimated_document_count() == 0
        assert await user_coll.add_doc(user) is None
        assert await user_coll.estimated_document_count() == 1
        #
        # Delete DB.
        Scruby.napalm()

    async def test_update_doc(self) -> None:
        """Testing a update_doc method."""
        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        assert await user_coll.estimated_document_count() == 0
        await user_coll.add_doc(user)
        assert await user_coll.estimated_document_count() == 1
        await user_coll.update_doc(user)
        assert await user_coll.estimated_document_count() == 1
        #
        # Delete DB.
        Scruby.napalm()

    async def test_get_key(self) -> None:
        """Testing a get_key method."""
        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        await user_coll.add_doc(user)
        data: User = await user_coll.get_doc("+447986123456")
        assert data.model_dump() == user.model_dump()
        assert data.phone == "+447986123456"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_has_key(self) -> None:
        """Testing a has_key method."""
        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        await user_coll.add_doc(user)
        assert await user_coll.has_key("+447986123456")
        assert not await user_coll.has_key("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_delete_key(self) -> None:
        """Testing a delete_key method."""
        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        assert await user_coll.estimated_document_count() == 0
        await user_coll.add_doc(user)
        assert await user_coll.estimated_document_count() == 1
        assert await user_coll.delete_doc("+447986123456") is None
        assert await user_coll.estimated_document_count() == 0
        assert not await user_coll.has_key("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_HASH_REDUCE_LEFT(self) -> None:
        """Length of reduction hash."""
        user_coll = await Scruby.collection(User)
        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )
        leaf_path, _ = await user_coll._get_leaf_path("key name")
        assert leaf_path == control_path

        Scruby.napalm()
        settings.HASH_REDUCE_LEFT = 2  # 16777216 branches in collection.
        user_coll = await Scruby.collection(User)
        control_path = Path(
            "ScrubyDB/User/a/6/d/2/d/1/leaf.json",
        )
        leaf_path, _ = await user_coll._get_leaf_path("key name")
        assert leaf_path == control_path

        Scruby.napalm()
        settings.HASH_REDUCE_LEFT = 4  # 65536 branches in collection.
        user_coll = await Scruby.collection(User)
        control_path = Path(
            "ScrubyDB/User/d/2/d/1/leaf.json",
        )
        leaf_path, _ = await user_coll._get_leaf_path("key name")
        assert leaf_path == control_path

        Scruby.napalm()
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection
        user_coll = await Scruby.collection(User)
        control_path = Path(
            "ScrubyDB/User/d/1/leaf.json",
        )
        leaf_path, _ = await user_coll._get_leaf_path("key name")
        assert leaf_path == control_path
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_one(self) -> None:
        """Find a single document."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await user_coll.add_doc(user)

        # by email
        result: User | None = await user_coll.find_one(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com",
        )
        assert result is not None
        assert result.email == "John_Smith_5@gmail.com"

        # by birthday
        result_2: User | None = await user_coll.find_one(
            filter_fn=lambda doc: doc.birthday == datetime(1970, 1, 8, tzinfo=ZoneInfo("UTC")),
        )
        assert result_2 is not None
        assert result_2.birthday == datetime(1970, 1, 8, tzinfo=ZoneInfo("UTC"))
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_many(self) -> None:
        """Find documents."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await user_coll.add_doc(user)

        # all arguments by default
        result_1: list[User] | None = await user_coll.find_many()
        assert result_1 is not None
        assert len(result_1) == 9

        # all args by default
        result_2: list[User] | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.email == "John_Smith_1@gmail.com" or doc.email == "John_Smith_9@gmail.com",
        )
        assert result_2 is not None
        assert len(result_2) == 2
        assert result_2[0].email in ["John_Smith_1@gmail.com", "John_Smith_9@gmail.com"]
        assert result_2[1].email in ["John_Smith_1@gmail.com", "John_Smith_9@gmail.com"]

        # limit docs = 5, page number = 1
        result_3: list[User] | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.last_name == "Smith",
            limit_docs=5,
            page_number=1,
        )
        assert result_3 is not None
        assert len(result_3) == 5

        # limit docs = 5, page number = 2
        result_4: list[User] | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.last_name == "Smith",
            limit_docs=5,
            page_number=2,
        )
        assert result_4 is not None
        assert len(result_4) == 4
        #
        # Delete DB.
        Scruby.napalm()

    async def test_collection_name(self) -> None:
        """Test a collection_name method."""
        user_coll = await Scruby.collection(User)

        assert user_coll.collection_name() == "User"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_count_documents(self) -> None:
        """Test a count_documents method."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await user_coll.add_doc(user)

        assert await user_coll.estimated_document_count() == 9
        result: int = await user_coll.count_documents(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert result == 2
        #
        # Delete DB.
        Scruby.napalm()

    async def test_delete_many(self) -> None:
        """Test a delete_many method."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await user_coll.add_doc(user)

        # by emails
        result: int = await user_coll.delete_many(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
        )
        assert result == 2
        assert await user_coll.estimated_document_count() == 7
        result = await user_coll.count_documents(
            filter_fn=lambda _: True,
        )
        assert result == 7
        #
        # Delete DB.
        Scruby.napalm()

    async def test_run_custom_task(self) -> None:
        """Test a run_custom_task method."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612345{num}",
            )
            await user_coll.add_doc(user)

        result = await user_coll.run_custom_task(
            custom_task_fn=custom_task,
            filter_fn=lambda doc: doc.first_name == "John",
        )
        assert result == 9
        #
        # Delete DB.
        Scruby.napalm()

    async def test_update_many(self) -> None:
        """Test a update_many method."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        for num in range(1, 10):
            user = User(
                first_name="John",
                last_name="Smith",
                birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
                email=f"John_Smith_{num}@gmail.com",
                phone=f"+44798612340{num}",
            )
            await user_coll.add_doc(user)

        number_updated_users = await user_coll.update_many(new_data={"first_name": "Georg"})
        assert number_updated_users == 9
        #
        # by email
        users: list[User] | None = await user_coll.find_many()
        assert users is not None
        for user in users:
            assert user.first_name == "Georg"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_extra_fields(self) -> None:
        """Test extra fields - `created_att` and `updated_at`."""
        settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection

        user_coll = await Scruby.collection(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123450",
        )
        await user_coll.add_doc(user)
        key = "+447986123450"
        result = await user_coll.get_doc(key)

        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)
        #
        # Delete DB.
        Scruby.napalm()
