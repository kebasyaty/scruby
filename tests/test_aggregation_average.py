"""Test a Average class."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

import pytest
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Average

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


def calculate_average_task(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
) -> Any:
    """Custom task.

    Calculate the average value.
    """
    max_workers: int | None = None
    timeout: float | None = None
    average_age: float = Average()

    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        for branch_number in branch_numbers:
            future = executor.submit(
                get_docs_fn,
                branch_number,
                hash_reduce_left,
                db_root,
                class_model,
            )
            docs = future.result(timeout)
            for doc in docs:
                average_age.set(doc.age)
    return average_age.get()


async def test_run_custom_task() -> None:
    """Test a run_custom_task method."""
    constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection (main purpose is tests).
    db = Scruby(User)

    for num in range(1, 10):
        user = User(
            first_name="John",
            age=f"{num * 10}",
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await db.set_key(f"+44798612345{num}", user)

    result = db.run_custom_task(calculate_average_task)
    assert result == 50.0
    #
    # Delete DB.
    await Scruby.napalm()
