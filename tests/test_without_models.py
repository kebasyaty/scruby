"""Test without models."""

from __future__ import annotations

import pytest

from scruby import Scruby, ScrubyConfig, Utils

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


def test_a_run_method() -> None:
    """Test a `run` method."""
    with pytest.raises(
        AssertionError,
        match=r"Create least one model of document for your project.",
    ):
        # Activate database.
        Scruby.run()


def test_db_collection_list() -> None:
    """Test a db_collection_list method."""
    assert Utils.db_collection_list(db_root=ScrubyConfig.db_root) is None
