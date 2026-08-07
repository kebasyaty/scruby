"""Test Database."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import pytest
from anyio import Path
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import ReturnType, Scruby, ScrubyModel
from scruby.errors import (
    KeyAlreadyExistsError,
    KeyNotExistsError,
)

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


class User(ScrubyModel):
    """User model."""

    first_name: str
    last_name: str
    birthday: datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class User2(ScrubyModel):
    """User model."""

    first_name: str
    last_name: str
    birthday: datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class User3(ScrubyModel):
    """User model."""

    username: str
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["username"],
        ),
    ]


class User4(ScrubyModel):
    """Key of Model is missing."""

    username: str


class TestNegative:
    """Negative tests."""

    async def test_model_key_is_missing(self) -> None:
        """Key of Model is missing."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        with pytest.raises(
            AssertionError,
            match=r"Model: User4 => The `key` field is missing.",
        ):
            Scruby(User4)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_add_doc_value_does_not_match_collection(self) -> None:
        """add_doc() - Parameter `value` does not match current collection."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user2 = User2(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        user_coll = Scruby(User)

        with pytest.raises(
            TypeError,
            match=r"Method: `add_doc` > Parameter: `doc` => Model `User2` does not match collection `User`!",
        ):
            await user_coll.add_doc(user2)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_update_doc_value_does_not_match_collection(self) -> None:
        """update_doc() - Parameter `value` does not match current collection."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

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

        user_coll = Scruby(User)
        await user_coll.add_doc(user)

        with pytest.raises(
            TypeError,
            match=r"Method: `update_doc` > Parameter: `doc` => Model `User2` does not match collection `User`!",
        ):
            await user_coll.update_doc(user2)
        #
        # Delete DB.
        Scruby.napalm()

    async def test_del_non_existent_key(self) -> None:
        """Delete a non-existent key."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

        with pytest.raises(KeyError):
            await user_coll.delete_doc("key missing")
        #
        # Delete DB.
        Scruby.napalm()

    async def test_key_is_empty(self) -> None:
        """The key should not be empty."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User3)

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
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
            match=r"Method: `find_many` => The `page_number` parameter must not be less than one.",
        ):
            await user_coll.find_many(
                filter_fn=lambda doc: doc.last_name == "Smith",
                limit_docs=5,
                page_number=0,
            )

        # limit docs = 5, page number = -1
        with pytest.raises(
            AssertionError,
            match=r"Method: `find_many` => The `page_number` parameter must not be less than one.",
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
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

        key_name = "key name"
        leaf_path, prepared_key = await user_coll._get_leaf_path(key_name)

        assert leaf_path == Path("ScrubyDB/User/1/leaf.dbm")
        assert prepared_key == key_name
        #
        # Delete DB.
        Scruby.napalm()

    async def test_collection_list(self) -> None:
        """Testing a `collection_list` methopd."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        Scruby(User)

        collection_list = Scruby.collection_list()
        assert collection_list is not None
        assert "User" in collection_list

        Scruby(User2)

        collection_list = Scruby.collection_list()
        assert collection_list is not None
        assert "User" in collection_list
        assert "User2" in collection_list
        #
        # Delete DB.
        Scruby.napalm()

    async def test_clear_collection(self) -> None:
        """Testing a `clear_collection` methopd."""
        # Activate database.
        Scruby.run()

        collection_list = Scruby.collection_list()
        assert collection_list is not None

        Scruby.clear_collection("User")
        collection_list = Scruby.collection_list()
        assert collection_list is not None
        assert "User" in collection_list
        assert "User2" in collection_list
        assert "User3" in collection_list
        assert "User4" in collection_list

        Scruby.clear_collection("User2")
        collection_list = Scruby.collection_list()
        assert collection_list is not None
        assert "User" in collection_list
        assert "User2" in collection_list
        assert "User3" in collection_list
        assert "User4" in collection_list
        #
        # Delete DB.
        Scruby.napalm()

    async def test_metadata(self) -> None:
        """Test metadata of collection."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

        meta = await user_coll.get_meta()
        assert meta.collection_name == "User"
        assert meta.hash_reduce_left == 7
        assert meta.max_number_branch == 16
        assert meta.counter_documents == 0

        meta.counter_documents = 1
        await user_coll._set_meta(meta)

        meta_2 = await user_coll.get_meta()
        assert meta_2.collection_name == "User"
        assert meta_2.hash_reduce_left == 7
        assert meta_2.max_number_branch == 16
        assert meta_2.counter_documents == 1
        #
        # Delete DB.
        Scruby.napalm()

    async def test_add_doc(self) -> None:
        """Testing a add_doc method."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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

    async def test_get_doc(self) -> None:
        """Testing a get_doc method."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone="+447986123456",
        )

        await user_coll.add_doc(user)
        data: User | None = await user_coll.get_doc("+447986123456")
        assert data.model_dump() == user.model_dump()
        assert data.phone == "+447986123456"

        # result is None
        assert await user_coll.get_doc("key missing") is None
        #
        # Delete DB.
        Scruby.napalm()

    async def test_has_key(self) -> None:
        """Testing a has_key method."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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

    async def test_hash_reduce_left(self) -> None:
        """Length of reduction hash."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)
        control_path = Path("ScrubyDB/User/1/leaf.dbm")
        leaf_path, _ = await user_coll._get_leaf_path("key name")
        assert leaf_path == control_path

        Scruby.napalm()
        user_coll = Scruby(User)
        control_path = Path("ScrubyDB/User/1/leaf.dbm")
        leaf_path, _ = await user_coll._get_leaf_path("key name")
        assert leaf_path == control_path
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_one(self) -> None:
        """Find a single document."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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

        # result is None
        result_3: User | None = await user_coll.find_one(
            filter_fn=lambda doc: doc.first_name == "???",
        )
        assert result_3 is None

        # include fields
        result_dict: dict | None = await user_coll.find_one(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com",
            include_fields={"email", "phone"},
            return_type=ReturnType.DICT,
        )
        assert result_dict is not None
        assert isinstance(result_dict, dict)
        assert len(result_dict) == 2
        assert result_dict["email"] == "John_Smith_5@gmail.com"
        assert result_dict["phone"] == "+447986123455"

        # exclude fields
        result_dict: dict | None = await user_coll.find_one(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com",
            exclude_fields={"key", "created_at", "updated_at", "first_name", "last_name", "birthday"},
            return_type=ReturnType.DICT,
        )
        assert result_dict is not None
        assert isinstance(result_dict, dict)
        assert len(result_dict) == 2
        assert result_dict["email"] == "John_Smith_5@gmail.com"
        assert result_dict["phone"] == "+447986123455"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_many(self) -> None:
        """Find documents."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
        result_1: list[User] | str | None = await user_coll.find_many()
        assert result_1 is not None
        assert len(result_1) == 9

        # all args by default
        result_2: list[User] | str | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.email == "John_Smith_1@gmail.com" or doc.email == "John_Smith_9@gmail.com",
        )
        assert result_2 is not None
        assert len(result_2) == 2
        assert result_2[0].email in ["John_Smith_1@gmail.com", "John_Smith_9@gmail.com"]
        assert result_2[1].email in ["John_Smith_1@gmail.com", "John_Smith_9@gmail.com"]

        # limit docs = 5, page number = 1
        result_3: list[User] | str | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.last_name == "Smith",
            limit_docs=5,
            page_number=1,
        )
        assert result_3 is not None
        assert len(result_3) == 5

        # limit docs = 5, page number = 2
        result_4: list[User] | str | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.last_name == "Smith",
            limit_docs=5,
            page_number=2,
        )
        assert result_4 is not None
        assert len(result_4) == 4

        # result is None
        result_5: list[User] | str | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.last_name == "???",
        )
        assert result_5 is None

        # include fields
        result_dict: list[User] | str | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com",
            include_fields={"email", "phone"},
            return_type=ReturnType.DICT,
        )
        assert result_dict is not None
        assert isinstance(result_dict[0], dict)
        assert len(result_dict[0]) == 2
        assert result_dict[0]["email"] == "John_Smith_5@gmail.com"
        assert result_dict[0]["phone"] == "+447986123455"

        # exclude fields
        result_dict: list[User] | str | None = await user_coll.find_many(
            filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com",
            exclude_fields={"key", "created_at", "updated_at", "first_name", "last_name", "birthday"},
            return_type=ReturnType.DICT,
        )
        assert result_dict is not None
        assert isinstance(result_dict[0], dict)
        assert len(result_dict[0]) == 2
        assert result_dict[0]["email"] == "John_Smith_5@gmail.com"
        assert result_dict[0]["phone"] == "+447986123455"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_collection_name(self) -> None:
        """Test a collection_name method."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

        assert user_coll.collection_name() == "User"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_count_documents(self) -> None:
        """Test a count_documents method."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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

    async def test_update_many(self) -> None:
        """Test a update_many method."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
        users: list[User] | str | None = await user_coll.find_many()
        assert users is not None
        for user in users:
            assert user.first_name == "Georg"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_extra_fields(self) -> None:
        """Test extra fields - `created_att` and `updated_at`."""
        # Delete DB.
        Scruby.napalm()

        # Activate database.
        Scruby.run()

        user_coll = Scruby(User)

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
