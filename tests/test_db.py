"""Test Stub."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="module")


class TestNegative:
    """Negative tests."""

    async def test_stub(self) -> None:
        """Testing stub."""
        assert True


class TestPositive:
    """Positive tests."""

    async def test_stub(self) -> None:
        """Testing stub."""
        assert True
