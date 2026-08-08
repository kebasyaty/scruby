#### Average

```py title="main.py" linenums="1"
"""Aggregation class for calculating the average value."""

import anyio
from decimal import ROUND_HALF_EVEN
from typing import Annotated, Any

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import (
    PhoneNumber,
    PhoneNumberValidator,
)

from scruby import CustomTask, Scruby, ScrubyModel
from scruby.aggregation import Average


class User(ScrubyModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]

class CalculateAverageAgeUsers(CustomTask):
    """Calculate the average age of users."""

    def __init__(self) -> None:
        """Initializing the task."""
        self.stop_signal = False
        self.average_age = Average(
            precision=".00",  # Default = .00
            rounding=ROUND_HALF_EVEN,  # Default = ROUND_HALF_EVEN
        )

    def accept(self, doc: Any) -> None:
        """Operation with a document."""
        self.average_age.set(doc.age)

    def result(self) -> Any | None:
        """Return result."""
        return float(self.average_age.get())


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run()

    # Get collection `User`.
    user_coll = Scruby(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(CalculateAverageAgeUsers())
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
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CustomTask, Scruby, ScrubyModel
from scruby.aggregation import Counter


class User(ScrubyModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class LimitUserSelection(CustomTask):
    """Limit user selection."""

    def __init__(self, limit_docs: int = 5) -> None:
        """Initializing the task."""
        self.stop_signal = False
        self.counter = Counter(limit=limit_docs)  # `limit` by default = 1000
        self.users: list[User] = []

    def accept(self, doc: Any) -> None:
        """Operation with a document."""
        if self.counter.check():
            self.stop_signal = True
            return
        self.users.append(doc)
        self.counter.next()

    def result(self) -> Any | None:
        """Return result."""
        return self.users


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run()

    # Get collection `User`.
    user_coll = Scruby(User)

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
        custom_task=LimitUserSelection(limit_docs=5),
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
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CustomTask, Scruby, ScrubyModel
from scruby.aggregation import Max


class User(ScrubyModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class CalculateMaxAgeUsers(CustomTask):
    """Calculate the maximum age of users."""

    def __init__(self) -> None:
        """Initializing the task."""
        self.stop_signal = False
        self.max_age = Max()

    def accept(self, doc: Any) -> None:
        """Operation with a document."""
        self.max_age.set(doc.age)

    def result(self) -> Any | None:
        """Return result."""
        return self.max_age.get()


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run()

    # Get collection `User`.
    user_coll = Scruby(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(CalculateMaxAgeUsers())
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
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CustomTask, Scruby, ScrubyModel
from scruby.aggregation import Min


class User(ScrubyModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class CalculateMinAgeUsers(CustomTask):
    """Calculate the minimum age of users."""

    def __init__(self) -> None:
        """Initializing the task."""
        self.stop_signal = False
        self.min_age = Min()

    def accept(self, doc: Any) -> None:
        """Operation with a document."""
        self.min_age.set(doc.age)

    def result(self) -> Any | None:
        """Return result."""
        return self.min_age.get()


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run()

    # Get collection `User`.
    user_coll = Scruby(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(CalculateMinAgeUsers())
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
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CustomTask, Scruby, ScrubyModel
from scruby.aggregation import Sum


class User(ScrubyModel):
    """User model."""

    first_name: str
    age: int
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


class CalculateTotalAgeUsers(CustomTask):
    """Calculate the total age of users."""

    def __init__(self) -> None:
        """Initializing the task."""
        self.stop_signal = False
        self.sum_age = Sum()

    def accept(self, doc: Any) -> None:
        """Operation with a document."""
        self.sum_age.set(doc.age)

    def result(self) -> Any | None:
        """Return result."""
        return int(self.sum_age.get())


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run()

    # Get collection `User`.
    user_coll = Scruby(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(CalculateTotalAgeUsers())
    print(result)  # => 450.0

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
