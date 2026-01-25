"""Testing Settings."""

from __future__ import annotations

from scruby import ScrubySettings


def test_db_root() -> None:
    """Test a DB_ROOT parameter."""
    assert ScrubySettings.db_root == "ScrubyDB"


def test_db_id() -> None:
    """ScrubySettings.db_id."""
    assert len(ScrubySettings.db_id) == 8


def test_hash_reduce_left() -> None:
    """Test a HASH_REDUCE_LEFT parameter."""
    assert ScrubySettings.hash_reduce_left == 6


def test_max_workers() -> None:
    """Test a MAX_WORKERS parameter."""
    assert ScrubySettings.max_workers is None


def test_plugins() -> None:
    """Test a PLUGINS parameter."""
    assert isinstance(ScrubySettings.plugins, list)
    assert len(ScrubySettings.plugins) == 0
