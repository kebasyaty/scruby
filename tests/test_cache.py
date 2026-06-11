"""Testing Cache."""

from __future__ import annotations

import pytest
from pydantic import Field

from scruby import Scruby, ScrubyModel

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
Scruby.napalm()


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


async def test_cache() -> None:
    """Testing Cache."""
