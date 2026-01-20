"""Test a Counter class in custom task."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, ScrubySettings
from scruby.aggregation import Counter

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
Scruby.napalm()


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


async def task_counter(
    search_task_fn: Callable,
    filter_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None = None,
    limit_docs=5,  # custom parameter
) -> list[User]:
    """Custom task.

    This task implements a counter of documents.
    """
    counter = Counter(limit=limit_docs)  # `limit` by default = 1000
    users: list[User] = []
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
            docs = await future.result()
            if docs is not None:
                for doc in docs:
                    if counter.check():
                        # [:limit_docs] - Control overflow in a multithreaded environment.
                        return users[:limit_docs]
                    users.append(doc)
                    counter.next()
    return users


async def test_task_counter() -> None:
    """Test a Counter class in custom task."""
    ScrubySettings.hash_reduce_left = 6  # 256 branches in collection
    coll_user = await Scruby.collection(User)

    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await coll_user.add_doc(user)

    result = await coll_user.run_custom_task(
        custom_task_fn=task_counter,
        limit_docs=5,  # optional
    )
    assert len(result) == 5

    result = await coll_user.run_custom_task(
        custom_task_fn=task_counter,
        filter_fn=lambda doc: doc.first_name == "John",
        limit_docs=5,  # custom parameter
    )
    assert len(result) == 5
    #
    # Delete DB.
    Scruby.napalm()
