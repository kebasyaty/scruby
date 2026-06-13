"""Test a Counter class in custom task."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from typing import Annotated, Any

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyConfig, ScrubyModel
from scruby.aggregation import Counter

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
Scruby.napalm()

# Activate database.
Scruby.run()


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
    max_workers: int | None,
    stop_signal: Event,
    limit_docs=5,  # custom parameter
) -> list[User]:
    """Custom task.

    This task implements a counter of documents.
    """
    stop_outer_loop: bool = False
    counter = Counter(limit=limit_docs)  # `limit` by default = 1000
    users: list[User] = []
    # Run quantum loop
    with ThreadPoolExecutor(max_workers) as executor:
        futures: list[Future] = [
            executor.submit(
                search_task_fn,
                branch_number,
                filter_fn,
                hash_reduce_left,
                db_root,
                class_model,
                stop_signal,
            )
            for branch_number in branch_numbers
        ]
        for future in as_completed(futures):
            docs = await future.result()
            if docs is not None:
                for doc in docs:
                    if counter.check():
                        # Cancel all pending tasks in the queue instantly
                        executor.shutdown(wait=False, cancel_futures=True)
                        # Trigger the event to tell running tasks to exit
                        stop_signal.set()
                        # Stop loops
                        stop_outer_loop = True
                        break
                    users.append(doc)
                    counter.next()
            if stop_outer_loop:
                break
    return users


async def test_task_counter() -> None:
    """Test a Counter class in custom task."""
    ScrubyConfig.hash_reduce_left = 6  # 256 branches in collection
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
