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


class UserProfile(BaseModel):
    """UserProfile model."""

    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


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


async def test_user_profile() -> None:
    """Test UserProfile 1."""
    # Get collection of `UserProfile`.
    user_profile_coll = await Scruby.create(UserProfile)

    # Create user profile.
    user = UserProfile(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    await user_profile_coll.add_key(user.phone, user)


async def test_user_profile_2() -> None:
    """Test UserProfile 1."""
    # Get collection of `UserProfile`.
    user_profile_coll = await Scruby.create(UserProfile)

    # Create user profile.
    user = UserProfile(
        first_name="John_2",
        last_name="Smith_2",
        birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
        email="John_Smith_2@gmail.com",
        phone="+447986123457",
    )

    await user_profile_coll.add_key(user.phone, user)
    #
    # Delete DB.
    Scruby.napalm()
