"""Testing Config."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyConfig, ScrubyModel

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


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


class Phone(ScrubyModel):
    """Phone model."""

    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    screen_diagonal: float = Field(strict=True)
    matrix_type: str = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


class Car(ScrubyModel):
    """Car model."""

    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    year: int = Field(strict=True)
    power_reserve: int = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


# Activate database.
Scruby.run(hash_reduce_left=0)


async def test_create_db() -> None:
    """Create a test database."""
    # Create users
    user_coll = await Scruby.collection(User)
    for num in range(9):
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone=f"+44798612345{num}",
        )
        # Add user to collection.
        await user_coll.add_doc(user)

    # Create phones
    phone_coll = await Scruby.collection(Phone)
    for num in range(9):
        phone = Phone(
            brand="Samsung",
            model=f"Galaxy A26 {num}",
            screen_diagonal=6.7,
            matrix_type="Super AMOLED",
        )
        # Add phone to collection.
        await phone_coll.add_doc(phone)

    # Create cars
    car_coll = await Scruby.collection(Car)
    for num in range(9):
        car = Car(
            brand="Mazda",
            model=f"EZ-6 {num}",
            year=2025,
            power_reserve=600,
        )
        # Add car to collection
        await car_coll.add_doc(car)


async def test_hash_reduce_left_0() -> None:
    """Testing the parameter hash_reduce_left = 0."""
    # Check Config
    assert ScrubyConfig.HASH_REDUCE_LEFT == 0
    assert ScrubyConfig.MAX_NUMBER_BRANCH == 4294967296

    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # collection_name
    assert user_coll.collection_name() == "User"

    # collection_list
    coll_list = await Scruby.collection_list()
    assert coll_list is not None
    for coll_name in coll_list:
        assert coll_name in ["User", "Phone", "Car"]

    # estimated_document_count
    assert await user_coll.estimated_document_count() == 9

    # add_doc
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123459",
    )
    await user_coll.add_doc(user)
    assert await user_coll.estimated_document_count() == 10

    # update_doc and get_doc
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1972, 11, 7, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123459",
    )
    await user_coll.update_doc(user)
    user: User | None = await user_coll.get_doc("+447986123459")
    assert user is not None
    assert user.birthday == datetime(1972, 11, 7, tzinfo=ZoneInfo("UTC"))

    # has_key
    assert await user_coll.has_key("+447986123459")

    # delete_doc
    await user_coll.delete_doc("+447986123459")
    assert not await user_coll.has_key("+447986123459")
    assert await user_coll.estimated_document_count() == 9
    #
    # delete_collection
    await Scruby.delete_collection("User")
    coll_list = await Scruby.collection_list()
    assert coll_list is not None
    for coll_name in coll_list:
        assert coll_name in ["Phone", "Car"]
    user_coll = await Scruby.collection(User)
    assert await user_coll.estimated_document_count() == 0
    coll_list = await Scruby.collection_list()
    assert coll_list is not None
    for coll_name in coll_list:
        assert coll_name in ["User", "Phone", "Car"]
    #
    # Delete DB.
    Scruby.napalm()
