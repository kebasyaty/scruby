"""Test inheritance."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

import pytest
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


class InvalidModel(BaseModel):
    """Invalid model type."""

    username: str
    first_name: str
    last_name: str
    birthday: datetime
    email: EmailStr
    phone: Annotated[
        PhoneNumber,
        PhoneNumberValidator(number_format="E164"),
        Field(strict=False),
    ]
    is_archival: Annotated[
        bool,
        Field(title="This is an archival document?", default=False),
    ]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class User(ScrubyModel):
    """User model."""

    username: str
    first_name: str
    last_name: str
    birthday: datetime
    email: EmailStr
    phone: Annotated[
        PhoneNumber,
        PhoneNumberValidator(number_format="E164"),
        Field(strict=False),
    ]
    is_archival: Annotated[
        bool,
        Field(title="This is an archival document?", default=False),
    ]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class InvalidUserProfile(User):
    """User profile model."""

    profession: str
    salary: int
    hobby: str


class Vehicle(BaseModel):
    """Vehicle model."""

    brand: Annotated[str, Field(frozen=True)]
    model: Annotated[str, Field(frozen=True)]
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


class CarType(StrEnum):
    """Car classification."""

    Sedan = "Sedan"
    Liftback = "Liftback"
    SUV = "SUV"
    Hatchback = "Hatchback"
    Coupe = "Coupe"
    Convertible = "Convertible"
    Pickup = "Pickup"
    Minivan = "Minivan"


class MotorcycleType(StrEnum):
    """Motorcycle classification."""

    Cruiser = "Cruiser"
    Sportbike = "Sportbike"
    Naked = "Naked"
    Touring = "Touring"
    Scooters = "Scooter"


class Car(ScrubyModel, Vehicle):
    """Car model."""

    type: Annotated[CarType, Field(title="Car classification")]


class Motorcycle(ScrubyModel, Vehicle):
    """Motorcycle model."""

    type: Annotated[MotorcycleType, Field(title="Motorcycle classification")]


# Activate database.
Scruby.run()


def test_inheritance_from_base_model() -> None:
    """Testing inheritance from BaseModel."""
    with pytest.raises(
        AssertionError,
        match=r"Scruby => Argument `class_model` does not contain the base class `ScrubyModel`.",
    ):
        # Access a user's profile collection
        Scruby(InvalidModel)


def test_indirect_inheritance_from_scruby_model() -> None:
    """Test indirect inheritance from ScrubyModel."""
    with pytest.raises(
        AssertionError,
        match=r"Scruby => Argument `class_model` does not contain the base class `ScrubyModel`.",
    ):
        # Access a user's profile collection
        Scruby(InvalidUserProfile)


@pytest.mark.asyncio
async def test_multiple_inheritance() -> None:
    """Multiple inheritance."""
    car_coll = Scruby(Car)
    car = Car(
        brand="Mazda",
        model="EZ-6",
        year=2025,
        power_reserve=600,
        type=CarType.Liftback,
    )
    await car_coll.add_doc(car)
    car_details: Car | None = car_coll.find_one(
        filter_fn=lambda doc: doc.model == "EZ-6",
    )
    assert car_details is not None
    assert car_details.brand == "Mazda"
    assert car_details.model == "EZ-6"
    assert car_details.year == 2025
    assert car_details.power_reserve == 600
    assert car_details.type == CarType.Liftback
    #
    motorcycle_coll = Scruby(Motorcycle)
    motorcycle = Motorcycle(
        brand="Wuxi Jose Electric",
        model="V9",
        year=2025,
        power_reserve=100,
        type=MotorcycleType.Sportbike,
    )
    await motorcycle_coll.add_doc(motorcycle)
    car_details: Car | None = motorcycle_coll.find_one(
        filter_fn=lambda doc: doc.model == "V9",
    )
    assert car_details is not None
    assert car_details.brand == "Wuxi Jose Electric"
    assert car_details.model == "V9"
    assert car_details.year == 2025
    assert car_details.power_reserve == 100
    assert car_details.type == MotorcycleType.Sportbike
    #
    # Delete DB.
    Scruby.napalm()
