"""Test Utils."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyConfig, ScrubyModel, Utils

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


def test_get_from_env() -> None:
    """Test a get_from_env method."""
    with pytest.raises(
        AssertionError,
        match=r"Utils - `get_from_env` => `key` must not be the empty string.",
    ):
        Utils.get_from_env(key="")


def test_add_to_env() -> None:
    """Test a add_to_env method."""
    with pytest.raises(
        AssertionError,
        match=r"Utils - `add_to_env` => `key` must not be the empty string.",
    ):
        Utils.add_to_env(key="", value="???")

    with pytest.raises(
        AssertionError,
        match=r"Utils - `add_to_env` => `value` must not be the empty string.",
    ):
        Utils.add_to_env(key="???", value="")


def test_db_collection_list() -> None:
    """Test a db_collection_list method."""
    with pytest.raises(
        AssertionError,
        match=r"Utils - `db_collection_list` => `db_root` must not be the empty string.",
    ):
        Utils.db_collection_list(db_root="")

    db_collection_list: list[str] | None = Utils.db_collection_list(db_root=ScrubyConfig.db_root)
    subclasses: list[Any] = [subclass.__name__ for subclass in ScrubyModel.__subclasses__()]

    assert db_collection_list is not None

    for collection_name in db_collection_list:
        assert collection_name in subclasses
    #
    # Delete DB.
    Scruby.napalm()
