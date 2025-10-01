"""Aggregation classes."""

from __future__ import annotations

__all__ = (
    "Average",
    "Max",
    "Min",
    "Sum",
)

from typing import Any


class Average:
    """Aggregation class for calculating the average value."""

    def __init__(self) -> None:  # noqa: D107
        self.value = 0.0
        self.counter = 0.0

    def set(self, number: int | float) -> None:
        """Add value.

        Args:
            number: Current value.
        """
        self.value += float(number)
        self.counter += 1.0

    def get(self) -> float:
        """Get arithmetic average value.

        Returns:
            Number (int|float) - Average value.
        """
        return self.value / self.counter


class Counter:
    """Aggregation class for calculating the number of documents.

    Args:
        max: The maximum counter value.
    """

    def __init__(self, max: int = 1000) -> None:
        self.max = max
        self.counter = 0

    def check(self) -> bool:
        """Check the condition of the counter.

        Returns:
            Boolean value. If `True`, the maximum value is achieved.
        """
        return self.counter == self.max

    def next(self) -> None:
        """Increment the counter on one."""
        self.counter += 1


class Max:
    """Aggregation class for calculating the maximum value."""

    def __init__(self) -> None:  # noqa: D107
        self.value: Any = 0

    def set(self, number: int | float) -> None:
        """Add value.

        Args:
            number: Current value.
        """
        if number > self.value:
            self.value = number

    def get(self) -> Any:
        """Get maximum value.

        Returns:
            Number (int|float) - Maximum value.
        """
        return self.value


class Min:
    """Aggregation class for calculating the minimum value."""

    def __init__(self) -> None:  # noqa: D107
        self.value: Any = 0

    def set(self, number: int | float) -> None:
        """Add value.

        Args:
            number: Current value.
        """
        if self.value == 0 or number < self.value:
            self.value = number

    def get(self) -> Any:
        """Get minimum value.

        Returns:
            Number (int|float) - Minimum value.
        """
        return self.value


class Sum:
    """Aggregation class for calculating sum of values."""

    def __init__(self) -> None:  # noqa: D107
        self.value: Any = 0

    def set(self, number: int | float) -> None:
        """Add value.

        Args:
            number: Current value.
        """
        self.value += number

    def get(self) -> Any:
        """Get sum of values.

        Returns:
            Number (int|float) - Sum of values.
        """
        return self.value
