"""Utilities."""

from __future__ import annotations

__all__ = (
    "get_from_env",
    "add_to_env",
)

from pathlib import Path

from dotenv import dotenv_values


def get_from_env(
    key: str,
    dotenv_path: Path | str = ".env",
) -> str | None:
    """Get value by key from .env file.

    Returns:
        None
    """
    value: str | None = None

    if isinstance(dotenv_path, str):
        dotenv_path = Path(dotenv_path)

    if dotenv_path.exists():
        env_dict: dict[str, str | None] = dotenv_values(dotenv_path)
        value = env_dict.get(key)

    return value


def add_to_env(
    key: str,
    value: str,
    dotenv_path: Path | str = ".env",
) -> str | None:
    """Add key-value to .env file.

    Returns:
        `value` or None
    """
    if isinstance(dotenv_path, str):
        dotenv_path = Path(dotenv_path)

    if dotenv_path.exists():
        env_dict: dict[str, str | None] = dotenv_values(dotenv_path)
        saved_value = env_dict.get(key)
        if saved_value is None:
            with dotenv_path.open("a+", encoding="utf-8") as env_file:
                content = f"\n{key}={value}"
                env_file.write(content)
        else:
            raise KeyError(f"add_to_env => Key `{key}` already exists.")
    else:
        target_dir = "/".join(str(dotenv_path).split("/")[:-1])
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        content = f"{key}={value}"
        dotenv_path.write_text(data=content, encoding="utf-8")

    return value
