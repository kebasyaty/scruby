"""Test inheritance."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

import pytest
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


# pyrefly: ignore [invalid-inheritance, not-a-type]
class InvalidModel(BaseModel):
    """Invalid model type."""

    username: str
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            strict=True,
            frozen=True,
            default_factory=lambda data: data["username"],
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
    #
    # Delete DB.
    Scruby.napalm()
