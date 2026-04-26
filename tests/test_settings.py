"""Testing Settings."""

from __future__ import annotations

from scruby import ScrubyConfig
from scruby.utils import get_from_env


def test_db_root() -> None:
    """Test a DB_ROOT parameter."""
    assert ScrubyConfig.db_root == "ScrubyDB"


def test_db_id() -> None:
    """ScrubyConfig.db_id."""
    ScrubyConfig.init_params()
    assert ScrubyConfig.db_id is not None
    assert len(ScrubyConfig.db_id) == 8
    delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
    db_id = get_from_env(key="id", dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta")
    assert db_id == ScrubyConfig.db_id


def test_hash_reduce_left() -> None:
    """Test a HASH_REDUCE_LEFT parameter."""
    assert ScrubyConfig.HASH_REDUCE_LEFT == 6


def test_max_workers() -> None:
    """Test a MAX_WORKERS parameter."""
    assert ScrubyConfig.max_workers is None


def test_plugins() -> None:
    """Test a PLUGINS parameter."""
    assert isinstance(ScrubyConfig.plugins, list)
    assert len(ScrubyConfig.plugins) == 0
