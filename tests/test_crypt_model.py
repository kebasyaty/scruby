"""Test CryptModel."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CryptModel, Scruby, ScrubyModel

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


class User(ScrubyModel, CryptModel):
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
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


async def test_crypt_model() -> None:
    """Test CryptModel."""
    # Activate database.
    Scruby.run()

    # Get access to the collection
    user_coll = Scruby(User)

    # Create user
    user = User(
        username="user_1",
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    test_pass = "user_pass_123"  # noqa: S105

    # Check for the presence of the `password` field
    assert "password" in list(User.model_fields.keys())

    # Check a password empty
    assert not user.password_is_valid(test_pass)

    # Add user to collection with password empty
    with pytest.raises(
        ValueError,
        match=r"Method: `add_doc` => The `password` field is empty",
    ):
        await user_coll.add_doc(user)

    # Add user password
    user.set_password(test_pass)

    # # Check a password
    assert user.password_is_valid(test_pass)

    # Add user to collection
    await user_coll.add_doc(user)

    # Get user details
    user = await user_coll.get_doc("+447986123456")
    #
    # Delete DB.
    Scruby.napalm()
