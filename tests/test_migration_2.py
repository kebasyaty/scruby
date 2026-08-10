"""Test Migration 2."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel


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


def test_migration_2() -> None:
    """Test Migration 2.

    Add collections and docs to databse.
    """
    # Activate database.
    Scruby.run()

    #
    collection_name_list: list[str] = [item.__name__ for item in ScrubyModel.__subclasses__()]
    assert "User" in collection_name_list
    assert "Phone" not in collection_name_list
    assert "Car" not in collection_name_list
    #
    # Delete DB.
    Scruby.napalm()
