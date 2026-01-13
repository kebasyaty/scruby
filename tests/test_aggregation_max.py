"""Test a Max class in custom task."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, settings
from scruby.aggregation import Max

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(ScrubyModel):
    """User model."""

    first_name: str = Field(strict=True)
    age: int = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


def task_calculate_max(
    search_task_fn: Callable,
    filter_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None = None,
) -> int:
    """Custom task.

    Calculate the max value.
    """
    max_age = Max()
    # Run quantum loop
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        for branch_number in branch_numbers:
            future = executor.submit(
                search_task_fn,
                branch_number,
                filter_fn,
                hash_reduce_left,
                db_root,
                class_model,
            )
            docs = future.result()
            if docs is not None:
                for doc in docs:
                    max_age.set(doc.age)
    return max_age.get()


async def test_task_calculate_max() -> None:
    """Test a Max class in custom task."""
    settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection
    user_coll = await Scruby.collection(User)

    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = user_coll.run_custom_task(task_calculate_max)
    assert result == 90.0
    #
    # Delete DB.
    Scruby.napalm()
