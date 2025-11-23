"""Testing Constants."""

from __future__ import annotations

from scruby.constants import DB_ROOT, HASH_REDUCE_LEFT


def test_db_root() -> None:
    """Test a DB_ROOT variable."""
    assert DB_ROOT == "ScrubyDB"


def test_HASH_REDUCE_LEFT() -> None:
    """Test a HASH_REDUCE_LEFT variable."""
    assert HASH_REDUCE_LEFT == 6
