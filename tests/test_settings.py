"""Testing Settings."""

from __future__ import annotations

from scruby import ScrubySettings
from scruby.utils import get_from_env


def test_db_root() -> None:
    """Test a DB_ROOT parameter."""
    assert ScrubySettings.db_root == "ScrubyDB"


def test_db_id() -> None:
    """ScrubySettings.db_id."""
    ScrubySettings.init_db_id()
    assert ScrubySettings.db_id is not None
    assert len(ScrubySettings.db_id) == 8
    db_id = get_from_env(key="id", dotenv_path=f"{ScrubySettings.db_root}/.env.meta")
    assert db_id == ScrubySettings.db_id


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
