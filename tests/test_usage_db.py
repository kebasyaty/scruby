"""Test usage of database."""

from __future__ import annotations

import datetime
from typing import Annotated

import pytest
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


class Phone(BaseModel):
    """Phone model."""

    brand: str
    model: str
    screen_diagonal: float
    matrix_type: str


class Car(BaseModel):
    """Car model."""

    brand: str
    model: str
    year: int
    power_reserve: int


async def test_user() -> None:
    """Test User 1."""
    # Get collection of `User`.
    user_coll = await Scruby.create(User)

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    await user_coll.add_key(user.phone, user)


async def test_user_2() -> None:
    """Test User 2."""
    # Get collection of `User`.
    user_coll = await Scruby.create(User)

    # Create user.
    user = User(
        first_name="John_2",
        last_name="Smith_2",
        birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
        email="John_Smith_2@gmail.com",
        phone="+447986123457",
    )

    await user_coll.add_key(user.phone, user)


async def test_phone() -> None:
    """Test Phone."""
    # Get collection of `Phone`.
    phone_coll = await Scruby.create(Phone)

    # Create phone.
    phone = Phone(
        brand="Samsung",
        model="Galaxy A26",
        screen_diagonal=6.7,
        matrix_type="Super AMOLED",
    )

    key = f"{phone.brand}-{phone.model}"
    await phone_coll.add_key(key, phone)


async def test_car() -> None:
    """Test Car."""
    # Get collection of `Car`.
    car_coll = await Scruby.create(Car)

    # Create car.
    car = Car(
        brand="Mazda",
        model="EZ-6",
        year=2025,
        power_reserve=600,
    )

    key = f"{car.brand}-{car.model}"
    await car_coll.add_key(key, car)
    #
    # Delete DB.
    Scruby.napalm()
