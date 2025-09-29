"""Aggregation classes."""

from __future__ import annotations

__all__ = (
    "Sum",
    "Max",
)

from typing import Any


class Sum:
    """Aggregation class for calculating sum."""

    def __init__(self) -> None:  # noqa: D107
        self.value: Any = 0

    def set(self, number: int | float) -> None:
        """Add value."""
        self.value += number

    def get(self) -> Any:
        """Get sum."""
        return self.value


class Max:
    """Aggregation class for calculating the maximum number."""

    def __init__(self) -> None:  # noqa: D107
        self.value: Any = 0

    def set(self, number: int | float) -> None:
        """Add value."""
        if number > self.value:
            self.value = number

    def get(self) -> Any:
        """Get maximum number."""
        return self.value


class Min:
    """Aggregation class for calculating the minimum number."""

    def __init__(self) -> None:
        self.value: Any = 0

    def set(self, number: int | float) -> None:
        """Add value."""
        if self.value == 0 or number < self.value:
            self.value = number

    def get(self) -> Any:
        """Get minimum number."""
        return self.value


class Average:
    """Aggregation class for calculating the arithmetic average number."""

    def __init__(self) -> None:
        self.value = 0.0
        self.counter = 0.0

    def set(self, number: int | float) -> None:
        """Add value."""
        self.value += float(number)
        self.counter += 1.0

    def get(self) -> float:
        """Get arithmetic average number."""
        return self.value / self.counter
