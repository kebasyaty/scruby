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


async def custom_task(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None = None,
) -> Any:
    """Custom task.

    Calculate the number of users named John.
    """
    counter: int = 0
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
                if doc.first_name == "John":
                    counter += 1
    return counter


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

    result = await user_coll.run_custom_task(custom_task)
    print(result)  # => 9

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
