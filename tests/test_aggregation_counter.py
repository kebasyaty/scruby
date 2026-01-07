"""Test a Counter class in custom task."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Any

import pytest
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, settings
from scruby.aggregation import Counter

pytestmark = pytest.mark.asyncio(loop_scope="module")


class User(BaseModel):
    """User model."""

    first_name: str = Field(strict=True)
    age: int = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # Extra fields
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def task_counter(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None = None,
) -> list[User]:
    """Custom task.

    This task implements a counter of documents.
    """
    limit_docs = 1000
    counter = Counter(limit=limit_docs)  # `limit` by default = 1000
    users: list[User] = []
    # Run quantum loop
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
                if counter.check():
                    # [:limit_docs] - Control overflow in a multithreaded environment.
                    return users[:limit_docs]
                users.append(doc)
                counter.next()
    return users


async def test_task_counter() -> None:
    """Test a Counter class in custom task."""
    settings.HASH_REDUCE_LEFT = 6  # 256 branches in collection
    db = await Scruby.collection(User)

    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await db.add_doc(user)

    result = await db.run_custom_task(
        custom_task_fn=task_counter,
        limit_docs=5,
    )
    assert len(result) == 5
    #
    # Delete DB.
    Scruby.napalm()
