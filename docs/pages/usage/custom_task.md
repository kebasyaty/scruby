#### Run custom task

```py title="main.py" linenums="1"
"""Custom task.

This method running a task created on the basis of a quantum loop.
Effectiveness running task depends on the number of processor threads.
"""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from typing import Annotated, Any
from collections.abc import Callable
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel, ScrubyConfig
from scruby.aggregation import Counter

ScrubyConfig.db_root = "ScrubyDB"  # Default = "ScrubyDB"
ScrubyConfig.HASH_REDUCE_LEFT = 3  # Default = 3
ScrubyConfig.max_workers = None  # Default = None
ScrubyConfig.plugins = []  # Default = []


class User(ScrubyModel):
    """User model."""
    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime = Field(strict=True)
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
    HASH_REDUCE_LEFT: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None,
    stop_signal: Event,
    limit_docs: int = 1000,  # custom parameter
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


async def main() -> None:
    """Example."""
    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(
        custom_task_fn=task_counter,
        filter_fn=lambda doc: doc.first_name == "John",
        limit_docs=5,  # custom parameter
    )
    print(result)  # => 9

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
