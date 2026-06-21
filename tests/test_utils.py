"""Test Utils."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel
from scruby.utils import Utils

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
    #
    # Delete DB.
    Scruby.napalm()
