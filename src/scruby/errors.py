"""XLOT Exceptions."""

from __future__ import annotations

__all__ = ("MetadataValueError",)


class ScrubyException(Exception):
    """Root Custom Exception."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)


class MetadataValueError(ScrubyException):
    """Exception is raised if value of variable in metadata does not matching expected."""

    def __init__(self, message: str) -> None:  # noqa: D107
        self.message = message
        super().__init__(self.message)
