"""Test usage of database."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel

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


class Phone(ScrubyModel):
    """Phone model."""

    brand: str = Field(frozen=True)
    model: str = Field(frozen=True)
    screen_diagonal: float
    matrix_type: str
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: f"{data['brand']}:{data['model']}",
        ),
    ]


class Car(ScrubyModel):
    """Car model."""

    brand: str = Field(frozen=True)
    model: str = Field(frozen=True)
    year: int
    power_reserve: int
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: f"{data['brand']}:{data['model']}",
        ),
    ]


# Activate database.
Scruby.run()


async def test_user() -> None:
    """Test User 1."""
    # Get collection `User`.
    user_coll = Scruby(User)

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    await user_coll.add_doc(user)


async def test_user_2() -> None:
    """Test User 2."""
    # Get collection `User`.
    user_coll = Scruby(User)

    # Create user.
    user = User(
        first_name="John_2",
        last_name="Smith_2",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith_2@gmail.com",
        phone="+447986123457",
    )

    await user_coll.add_doc(user)


async def test_phone() -> None:
    """Test Phone."""
    # Get collection `Phone`.
    phone_coll = Scruby(Phone)

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
    # Get collection `Car`.
    car_coll = Scruby(Car)

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
