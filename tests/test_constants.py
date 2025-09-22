"""Testing Constants."""

from __future__ import annotations

from scruby.constants import DB_ROOT, LENGTH_SEPARATED_HASH


def test_db_root() -> None:
    """Test a DB_ROOT variable."""
    assert DB_ROOT == "ScrubyDB"


def test_length_separated_hash() -> None:
    """Test a LENGTH_SEPARATED_HASH variable."""
    assert LENGTH_SEPARATED_HASH == 0
