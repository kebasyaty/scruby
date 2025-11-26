#### Average

```py title="main.py" linenums="1"
"""Aggregation class for calculating the average value."""

import anyio
import concurrent.futures
from collections.abc import Callable
from decimal import ROUND_HALF_EVEN
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Average

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


def task_calculate_average(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    limit_docs: int,
) -> float:
    """Custom task.

    Calculate the average value.
    """
    max_workers: int | None = None
    timeout: float | None = None
    average_age = Average(
        precision=".00",           # by default = .00
        rounding=ROUND_HALF_EVEN,  # by default = ROUND_HALF_EVEN
    )

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
    return float(average_age.get())


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
        await user_coll.add_key(user.phone, user)

    result = user_coll.run_custom_task(task_calculate_average)
    print(result)  # => 50.0

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Counter

```py title="main.py" linenums="1"
"""Aggregation class for calculating sum of values."""

import anyio
import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Counter

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


def task_counter(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    limit_docs: int,
) -> list[User]:
    """Custom task.

    This task implements a counter of documents.
    """
    max_workers: int | None = None
    timeout: float | None = None
    users: list[User] = []
    counter = Counter(limit=limit_docs)  # `limit` by default = 1000

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
                if counter.check():
                    # [:limit_docs] - Control overflow in a multithreaded environment.
                    return users[:limit_docs]
                users.append(doc)
                counter.next()
    return users


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
        await user_coll.add_key(user.phone, user)

    result = user_coll.run_custom_task(
        custom_task_fn=task_counter,
        limit_docs=5,
    )
    print(len(result))  # => 5

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Max

```py title="main.py" linenums="1"
"""Aggregation class for calculating the maximum value."""

import anyio
import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Max

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


def task_calculate_max(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    limit_docs: int,
) -> int:
    """Custom task.

    Calculate the max value.
    """
    max_workers: int | None = None
    timeout: float | None = None
    max_age = Max()

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
                max_age.set(doc.age)
    return max_age.get()


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
        await user_coll.add_key(user.phone, user)

    result = user_coll.run_custom_task(task_calculate_max)
    print(result)  # => 90.0

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Min

```py title="main.py" linenums="1"
"""Aggregation class for calculating the minimum value."""

import anyio
import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Min

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


def task_calculate_min(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    limit_docs: int,
) -> int:
    """Custom task.

    Calculate the min value.
    """
    max_workers: int | None = None
    timeout: float | None = None
    min_age = Min()

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
                min_age.set(doc.age)
    return min_age.get()


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
        await user_coll.add_key(user.phone, user)

    result = user_coll.run_custom_task(task_calculate_min)
    print(result)  # => 10.0

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Sum

```py title="main.py" linenums="1"
"""Aggregation class for calculating sum of values."""

import anyio
import concurrent.futures
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, constants
from scruby.aggregation import Sum

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


def task_calculate_sum(
    get_docs_fn: Callable,
    branch_numbers: range,
    hash_reduce_left: int,
    db_root: str,
    class_model: Any,
    limit_docs: int,
) -> int:
    """Custom task.

    Calculate the sum of values.
    """
    max_workers: int | None = None
    timeout: float | None = None
    sum_age = Sum()

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
                sum_age.set(doc.age)
    return int(sum_age.get())


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
        await user_coll.add_key(user.phone, user)

    result = user_coll.run_custom_task(task_calculate_sum)
    print(result)  # => 450.0

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
