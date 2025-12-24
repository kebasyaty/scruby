"""Test usage of database."""

from __future__ import annotations

import datetime
from typing import Annotated

import pytest
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime.datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


class Phone(BaseModel):
    """Phone model."""

    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    screen_diagonal: float = Field(strict=True)
    matrix_type: str = Field(strict=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


class Car(BaseModel):
    """Car model."""

    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    year: int = Field(strict=True)
    power_reserve: int = Field(strict=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


async def test_user() -> None:
    """Test User 1."""
    # Get collection of `User`.
    user_coll = await Scruby.collection(User)

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    await user_coll.add_doc(user)


async def test_user_2() -> None:
    """Test User 2."""
    # Get collection of `User`.
    user_coll = await Scruby.collection(User)

    # Create user.
    user = User(
        first_name="John_2",
        last_name="Smith_2",
        birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
        email="John_Smith_2@gmail.com",
        phone="+447986123457",
    )

    await user_coll.add_doc(user)


async def test_phone() -> None:
    """Test Phone."""
    # Get collection of `Phone`.
    phone_coll = await Scruby.collection(Phone)

    # Create phone.
    phone = Phone(
        brand="Samsung",
        model="Galaxy A26",
        screen_diagonal=6.7,
        matrix_type="Super AMOLED",
    )

    # Add phone to collection.
    await phone_coll.add_doc(phone)


async def test_car() -> None:
    """Test Car."""
    # Get collection of `Car`.
    car_coll = await Scruby.collection(Car)

    # Create car.
    car = Car(
        brand="Mazda",
        model="EZ-6",
        year=2025,
        power_reserve=600,
    )

    # Add car to collection.
    await car_coll.add_doc(car)
    #
    # Delete DB.
    Scruby.napalm()
