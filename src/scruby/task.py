"""Tools for custom tasks."""

from __future__ import annotations

__all__ = ("CustomTask",)

from abc import ABC, abstractmethod
from typing import Any


class CustomTask(ABC):
    """Abstract class of custom tasks."""

    def __init__(self, **kwargs) -> None:
        """Initializing the task."""
        self.stop_signal = False

        for key, val in kwargs.items():
            self.__dict__[key] = val

    @abstractmethod
    def accept(self, doc: Any) -> None:
        """Operation with a document."""

    @abstractmethod
    def result(self) -> Any | None:
        """Return result."""
