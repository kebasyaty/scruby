"""Test without models."""

from __future__ import annotations

import pytest

from scruby import Scruby

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


def test_a_run_method() -> None:
    """Test a `run` method."""
    # Activate database.
    with pytest.raises(
        AssertionError,
        match=r"Create least one model of document for your project.",
    ):
        Scruby.run()
