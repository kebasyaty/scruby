"""Testing Cache."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel
from scruby.cache import DocCache

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
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
Scruby.run(db_root="TestScrubyDB")


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


async def test_user() -> None:
    """Test User."""
    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # collection_name
    assert user_coll.collection_name() == "User"

    # collection_list
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]

    # estimated_document_count
    assert await user_coll.estimated_document_count() == 9
    # count_documents
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 9

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
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 10

    #
    # delete_collection
    await Scruby.delete_collection("User")
    assert DocCache.cache.get("User") is None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["Phone", "Car"]
    user_coll = await Scruby.collection(User)
    assert await user_coll.estimated_document_count() == 0
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 0
    assert DocCache.cache.get("User") is not None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]


async def test_phone() -> None:
    """Test Phone."""
    # Get collection `Phone`.
    phone_coll = await Scruby.collection(Phone)

    # collection_name
    assert phone_coll.collection_name() == "Phone"

    # collection_list
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]

    # estimated_document_count
    assert await phone_coll.estimated_document_count() == 9
    # count_documents
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 9

    # add_doc
    phone = Phone(
        brand="Samsung",
        model="Galaxy A26 9",
        screen_diagonal=6.7,
        matrix_type="Super AMOLED",
    )
    await phone_coll.add_doc(phone)
    assert await phone_coll.estimated_document_count() == 10
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 10

    #
    # delete_collection
    await Scruby.delete_collection("Phone")
    assert DocCache.cache.get("Phone") is None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Car"]
    phone_coll = await Scruby.collection(Phone)
    assert await phone_coll.estimated_document_count() == 0
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 0
    assert DocCache.cache.get("Phone") is not None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]


async def test_car() -> None:
    """Test Car."""
    # Get collection `Car`.
    car_coll = await Scruby.collection(Car)

    # collection_name
    assert car_coll.collection_name() == "Car"

    # collection_list
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]

    # estimated_document_count
    assert await car_coll.estimated_document_count() == 9
    # count_documents
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 9

    # add_doc
    car = Car(
        brand="Mazda",
        model="EZ-6 9",
        year=2025,
        power_reserve=600,
    )
    await car_coll.add_doc(car)
    assert await car_coll.estimated_document_count() == 10
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 10

    #
    # delete_collection
    await Scruby.delete_collection("Car")
    assert DocCache.cache.get("Car") is None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone"]
    car_coll = await Scruby.collection(Car)
    assert await car_coll.estimated_document_count() == 0
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 0
    assert DocCache.cache.get("Car") is not None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]
    #
    # Delete DB.
    Scruby.napalm()
