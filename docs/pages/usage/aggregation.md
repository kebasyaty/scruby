#### Average

```py title="main.py" linenums="1"
"""Aggregation class for calculating the average value."""

import anyio
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from collections.abc import Callable
from decimal import ROUND_HALF_EVEN
from typing import Annotated, Any

from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, ScrubyConfig
from scruby.aggregation import Average


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


async def task_calculate_average(
    search_task_fn: Callable,
    filter_fn: Callable,
    branch_numbers: range,
    HASH_REDUCE_LEFT: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None,
    stop_signal: Event,
) -> float:
    """Custom task.

    Calculate the average value.
    """
    average_age = Average(
        precision=".00",           # Default = .00
        rounding=ROUND_HALF_EVEN,  # Default = ROUND_HALF_EVEN
    )
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
                    average_age.set(doc.age)
    return float(average_age.get())


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run(
        db_root = "ScrubyDB",  # Default = "ScrubyDB"
        HASH_REDUCE_LEFT = 6,  # Default = 6
        max_workers = None,  # Default = None
        plugins = None,  # Default = None
    )

    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(task_calculate_average)
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
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, ScrubyConfig
from scruby.aggregation import Counter


class User(BaseModel):
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
    # Activate database.
    Scruby.run(
        db_root = "ScrubyDB",  # Default = "ScrubyDB"
        HASH_REDUCE_LEFT = 6,  # Default = 6
        max_workers = None,  # Default = None
        plugins = None,  # Default = None
    )

    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(
        custom_task_fn=task_counter,
        limit_docs=5,  # custom parameter
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
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, ScrubyConfig
from scruby.aggregation import Max


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


async def task_calculate_max(
    search_task_fn: Callable,
    filter_fn: Callable,
    branch_numbers: range,
    HASH_REDUCE_LEFT: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None,
    stop_signal: Event,
) -> int:
    """Custom task.

    Calculate the max value.
    """
    max_age = Max()
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
                    max_age.set(doc.age)
    return max_age.get()


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run(
        db_root = "ScrubyDB",  # Default = "ScrubyDB"
        HASH_REDUCE_LEFT = 6,  # Default = 6
        max_workers = None,  # Default = None
        plugins = None,  # Default = None
    )

    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(task_calculate_max)
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
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, ScrubyConfig
from scruby.aggregation import Min


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


async def task_calculate_min(
    search_task_fn: Callable,
    filter_fn: Callable,
    branch_numbers: range,
    HASH_REDUCE_LEFT: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None,
    stop_signal: Event,
) -> int:
    """Custom task.

    Calculate the min value.
    """
    min_age = Min()
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
                    min_age.set(doc.age)
    return min_age.get()


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run(
        db_root = "ScrubyDB",  # Default = "ScrubyDB"
        HASH_REDUCE_LEFT = 6,  # Default = 6
        max_workers = None,  # Default = None
        plugins = None,  # Default = None
    )

    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(task_calculate_min)
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
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event
from collections.abc import Callable
from typing import Annotated, Any

from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel, ScrubyConfig
from scruby.aggregation import Sum


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


async def task_calculate_sum(
    search_task_fn: Callable,
    filter_fn: Callable,
    branch_numbers: range,
    HASH_REDUCE_LEFT: int,
    db_root: str,
    class_model: Any,
    max_workers: int | None,
    stop_signal: Event,
) -> int:
    """Custom task.

    Calculate the sum of values.
    """
    sum_age = Sum()
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
                    sum_age.set(doc.age)
    return int(sum_age.get())


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run(
        db_root = "ScrubyDB",  # Default = "ScrubyDB"
        HASH_REDUCE_LEFT = 6,  # Default = 6
        max_workers = None,  # Default = None
        plugins = None,  # Default = None
    )

    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(task_calculate_sum)
    print(result)  # => 450.0

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
