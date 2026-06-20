"""Testing Config."""

from __future__ import annotations

from scruby import Scruby, ScrubyConfig
from scruby.utils import Utils

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


class TestConfigParams:
    """Testing configuration parameters."""

    def test_db_id(self) -> None:
        """ScrubyConfig.db_id."""
        assert ScrubyConfig.db_id is None

    def test_db_root(self) -> None:
        """Test a DB_ROOT parameter."""
        assert ScrubyConfig.db_root == "ScrubyDB"

    def test_hash_reduce_left(self) -> None:
        """Test a HASH_REDUCE_LEFT parameter."""
        assert ScrubyConfig.HASH_REDUCE_LEFT == 7

    def test_max_number_branch(self) -> None:
        """Test a MAX_NUMBER_BRANCH parameter."""
        assert ScrubyConfig.MAX_NUMBER_BRANCH == 16

    def test_max_workers(self) -> None:
        """Test a MAX_WORKERS parameter."""
        assert ScrubyConfig.max_workers is None

    def test_plugins(self) -> None:
        """Test a PLUGINS parameter."""
        assert ScrubyConfig.plugins is None


class TestConfigMethods:
    """Testing configuration methods."""

    def test_init_db_id(self) -> None:
        """Test a init_db_id method."""
        ScrubyConfig.init_db_id()
        assert ScrubyConfig.db_id is not None
        assert len(ScrubyConfig.db_id) == 8
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        db_id = Utils.get_from_env(key="db_id", dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta")
        assert db_id == ScrubyConfig.db_id
        #
        # Delete DB.
        Scruby.napalm()

    def test_init_max_number_branch(self) -> None:
        """Test a init_max_number_branch method."""
        # 7
        ScrubyConfig.HASH_REDUCE_LEFT = 7
        ScrubyConfig.init_max_number_branch()
        assert ScrubyConfig.MAX_NUMBER_BRANCH == 16
        # 6
        ScrubyConfig.HASH_REDUCE_LEFT = 6
        ScrubyConfig.init_max_number_branch()
        assert ScrubyConfig.MAX_NUMBER_BRANCH == 256
        # 5
        ScrubyConfig.HASH_REDUCE_LEFT = 5
        ScrubyConfig.init_max_number_branch()
        assert ScrubyConfig.MAX_NUMBER_BRANCH == 4096
        # 0
        ScrubyConfig.HASH_REDUCE_LEFT = 0
        ScrubyConfig.init_max_number_branch()
        assert ScrubyConfig.MAX_NUMBER_BRANCH == 4294967296
        #
        # Delete DB.
        Scruby.napalm()

    def test_check_hash_reduce_left(self) -> None:
        """Test a check_hash_reduce_left method."""
        # 7
        test_num = 7
        ScrubyConfig.HASH_REDUCE_LEFT = test_num
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        # repeat
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        #
        # Delete DB.
        Scruby.napalm()
        #
        # 6
        test_num = 6
        ScrubyConfig.HASH_REDUCE_LEFT = test_num
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        # repeat
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        #
        # Delete DB.
        Scruby.napalm()
        #
        # 5
        test_num = 5
        ScrubyConfig.HASH_REDUCE_LEFT = test_num
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        # repeat
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        #
        # Delete DB.
        Scruby.napalm()
        #
        # 0
        test_num = 0
        ScrubyConfig.HASH_REDUCE_LEFT = test_num
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        # repeat
        ScrubyConfig.check_hash_reduce_left()
        delimiter: str = "/" if ScrubyConfig.sys_platform != "win32" else ""
        hash_reduce_left = Utils.get_from_env(
            key="hash_reduce_left",
            dotenv_path=f"{ScrubyConfig.db_root}{delimiter}.env.meta",
        )
        assert hash_reduce_left is not None
        assert int(hash_reduce_left) == test_num
        #
        # Delete DB.
        Scruby.napalm()
