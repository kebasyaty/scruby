"""Testing Constants."""

from __future__ import annotations

from scruby.constants import DB_ROOT, LENGTH_REDUCTION_HASH


def test_db_root() -> None:
    """Test a DB_ROOT variable."""
    assert DB_ROOT == "ScrubyDB"


def test_LENGTH_REDUCTION_HASH() -> None:
    """Test a LENGTH_REDUCTION_HASH variable."""
    assert LENGTH_REDUCTION_HASH == 0
