"""Test a Average class in custom task."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from decimal import ROUND_HALF_EVEN
from typing import Annotated, Any

import pytest
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Average

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str = Field(strict=True)
    age: int = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def task_calculate_average(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    limit_docs: int,  # noqa: ARG001
) -> float:
    """Custom task.

    Calculate the average value.
    """
    max_workers: int | None = None
    average_age = Average(
        precision=".00",  # by default = .00
        rounding=ROUND_HALF_EVEN,  # by default = ROUND_HALF_EVEN
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        for branch_number in branch_numbers:
            future = executor.submit(
                get_docs_fn,
                branch_number,
                hash_reduce_left,
                db_root,
                class_model,
            )
            docs = await future.result()
            for doc in docs:
                average_age.set(doc.age)
    return float(average_age.get())


async def test_task_calculate_average() -> None:
    """Test a Average class in custom task."""
    constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
    db = await Scruby.create(User)

    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await db.add_doc(user)

    result = await db.run_custom_task(task_calculate_average)
    assert result == 50.0
    #
    # Delete DB.
    Scruby.napalm()
