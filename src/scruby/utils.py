"""Utilities."""

from __future__ import annotations

__all__ = ("Utils",)


from pathlib import Path

from dotenv import dotenv_values


class Utils:
    """Set of helper methods."""

    @staticmethod
    def get_from_env(
        key: str,
        dotenv_path: Path | str = ".env",
    ) -> str | None:
        """Get value by key from .env file."""
        assert len(key) > 0, "`get_from_env` => `key` must not be the empty string."

        value: str | None = None

        if isinstance(dotenv_path, str):
            dotenv_path = Path(dotenv_path)

        if dotenv_path.exists():
            env_dict: dict[str, str | None] = dotenv_values(dotenv_path)
            value = env_dict.get(key)

        return value

    @staticmethod
    def add_to_env(
        key: str,
        value: str,
        dotenv_path: Path | str = ".env",
    ) -> str | None:
        """Add key-value to .env file."""
        assert len(key) > 0, "`add_to_env` => `key` must not be the empty string."
        assert len(value) > 0, "`add_to_env` => `value` must not be the empty string."

        if isinstance(dotenv_path, str):
            assert len(dotenv_path) > 0, "`add_to_env` => `dotenv_path` must not be the empty string."
            dotenv_path = Path(dotenv_path)

        if dotenv_path.exists():
            env_dict: dict[str, str | None] = dotenv_values(dotenv_path)
            saved_value = env_dict.get(key)
            if saved_value is None:
                with dotenv_path.open("a+", encoding="utf-8") as env_file:
                    content = f"\n{key}={value}"
                    env_file.write(content)
            else:
                raise KeyError(f"`add_to_env` => Key `{key}` already exists.")
        else:
            target_dir: str = "/".join(str(dotenv_path).split("/")[:-1])
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            content = f"{key}={value}"
            dotenv_path.write_text(data=content, encoding="utf-8")

        return value

    @staticmethod
    def db_collection_list(db_root: Path | str) -> list[str] | None:
        """Get a list of collections from a database directory."""
        if isinstance(db_root, str):
            assert len(db_root) > 0, "`add_to_env` => `dotenv_path` must not be the empty string."

        db_dir_path = Path(db_root)
        directory_names: list[str] | None = None
        if db_dir_path.exists():
            all_entries = Path.iterdir(db_dir_path)
            directory_names = [entry.name for entry in all_entries if entry.name != ".env.meta"] or None
        return directory_names
