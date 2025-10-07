#### Custom task

```py title="main.py" linenums="1"
"""Running custom task.

This method running a task created on the basis of a quantum loop.
Effectiveness running task depends on the number of processor threads.
Ideally, hundreds and even thousands of threads are required.
"""

import anyio
import datetime
import concurrent.futures
from typing import Annotated, Any
from collections.abc import Callable
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection
                                # (main purpose is tests).


class User(BaseModel):
    """Model of User."""
    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


def custom_task(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
) -> Any:
    """Custom task.

    Calculate the number of users named John.
    """
    max_workers: int | None = None
    timeout: float | None = None
    counter: int = 0

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
                if doc.first_name == "John":
                    counter += 1
    return counter


async def main() -> None:
    """Example."""
    # Get collection of `User`.
    user_coll = Scruby(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, num),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.set_key(user.phone, user)

    result = user_coll.run_custom_task(custom_task)
    print(result)  # => 9

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
