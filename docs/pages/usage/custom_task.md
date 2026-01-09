#### Custom task

```py title="main.py" linenums="1"
"""Running custom task.

This method running a task created on the basis of a quantum loop.
Effectiveness running task depends on the number of processor threads.
"""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
import concurrent.futures
from typing import Annotated, Any
from collections.abc import Callable
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel, settings
from scruby.aggregation import Counter

settings.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
settings.HASH_REDUCE_LEFT = 6  # By default = 6
settings.MAX_WORKERS = None  # By default = None


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
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None = None,
    limit_docs: int = 1000,  # custom parameter
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
                    if filter_fn(doc):
                        users.append(doc)
                        counter.next()
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
