"""Scruby Exceptions."""

from __future__ import annotations

__all__ = (
    "ScrubyException",
    "MetadataValueError",
)


class ScrubyException(Exception):
    """Root Custom Exception."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]  # noqa: D107
        super().__init__(*args, **kwargs)


class MetadataValueError(ScrubyException):
    """Exception is raised if value of variable in metadata does not matching expected."""

    def __init__(self, message: str) -> None:  # noqa: D107
        self.message = message
        super().__init__(self.message)


class KeyAlreadyExistsError(ScrubyException):
    """Exception is raised if the key already exists."""

    def __init__(self) -> None:
        self.message = "The key already exists."
        super().__init__(self.message)


class KeyNotExistsError(ScrubyException):
    """Exception is raised If the key is not exists."""

    def __init__(self) -> None:
        self.message = "The key not exists."
        super().__init__(self.message)
