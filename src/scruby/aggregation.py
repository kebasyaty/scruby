"""Aggregation classes."""

from __future__ import annotations

__all__ = (
    "Average",
    "Counter",
    "Max",
    "Min",
    "Sum",
)

from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any


class Average:
    """Aggregation class for calculating the average value.

    Args:
        precision: The accuracy of rounding. `By default = .00`
        rounding: Rounding mode. `By default = ROUND_HALF_EVEN`
    """

    def __init__(  # noqa: D107
        self,
        precision: str = ".00",
        rounding: str = ROUND_HALF_EVEN,
    ) -> None:
        self.value = Decimal()
        self.counter = 0
        self.precision = precision
        self.rounding = rounding

    def set(self, number: int | float) -> None:
        """Add value.

        Args:
            number: Current value (int | float).
        """
        self.value += Decimal(str(number))
        self.counter += 1

    def get(self) -> Decimal:
        """Get arithmetic average value.

        Returns:
            Number (Decimal) - Average value.
        """
        return (self.value / Decimal(str(self.counter))).quantize(
            exp=Decimal(self.precision),
            rounding=self.rounding,
        )


class Counter:
    """Aggregation class for calculating the number of documents.

    Args:
        limit: The maximum counter value.
    """

    def __init__(self, limit: int = 1000) -> None:  # noqa: D107
        self.limit = limit
        self.counter = 0

    def check(self) -> bool:
        """Check the condition of the counter.

        Returns:
            Boolean value. If `True`, the maximum value is achieved.
        """
        return self.counter >= self.limit

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
        self.value = Decimal()

    def set(self, number: int | float) -> None:
        """Add value.

        Args:
            number: Current value.
        """
        self.value += Decimal(str(number))

    def get(self) -> Decimal:
        """Get sum of values.

        Returns:
            Number (int|float) - Sum of values.
        """
        return self.value
