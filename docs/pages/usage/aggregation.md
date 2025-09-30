#### Average

```py title="main.py" linenums="1"
"""Aggregation class for calculating the arithmetic average number."""

import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Average

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection
                                # (main purpose is tests).

class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]
```

#### Max

```py title="main.py" linenums="1"
"""Aggregation class for calculating the maximum number."""

import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Max

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection
                                # (main purpose is tests).


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


async def main() -> None:
    """Example."""
    # Get collection of `User`.
    user_coll = Scruby(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=f"{num * 10}",
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await db.set_key(f"+44798612345{num}", user)

    result = db.run_custom_task(calculate_average_task)
    print(result)  # => 50.0

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Min

```py title="main.py" linenums="1"
"""Aggregation class for calculating the minimum number."""

import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Min

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection
                                # (main purpose is tests).

class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]
```

#### Sum

```py title="main.py" linenums="1"
"""Aggregation class for calculating sum."""

import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Sum

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection
                                # (main purpose is tests).

class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]
```
