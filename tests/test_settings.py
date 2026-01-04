"""Testing Settings."""

from __future__ import annotations

from scruby.settings import DB_ROOT, HASH_REDUCE_LEFT, MAX_WORKERS


def test_db_root() -> None:
    """Test a DB_ROOT parameter."""
    assert DB_ROOT == "ScrubyDB"


def test_hash_reduce_left() -> None:
    """Test a HASH_REDUCE_LEFT parameter."""
    assert HASH_REDUCE_LEFT == 6


def test_max_workers() -> None:
    """Test a MAX_WORKERS parameter."""
    assert MAX_WORKERS is None
