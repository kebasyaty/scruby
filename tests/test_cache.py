"""Testing Cache."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyConfig, ScrubyModel
from scruby.cache import DocCache

pytestmark = pytest.mark.asyncio(loop_scope="module")


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


ScrubyConfig.db_root = "TestScrubyDB"
ScrubyConfig.init_params()
DocCache.load_cache(ScrubyModel.__subclasses__())


async def test_user() -> None:
    """Test User."""
    # Get collection `User`.
    user_coll = await Scruby.collection(User)
    assert await user_coll.estimated_document_count() == 9
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 9


async def test_phone() -> None:
    """Test Phone."""
    # Get collection `Phone`.
    phone_coll = await Scruby.collection(Phone)
    assert await phone_coll.estimated_document_count() == 9
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 9


async def test_car() -> None:
    """Test Car."""
    # Get collection `Car`.
    car_coll = await Scruby.collection(Car)
    assert await car_coll.estimated_document_count() == 9
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 9
