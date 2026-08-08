"""Test a Counter class in custom task."""

from __future__ import annotations

from typing import Annotated, Any

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CustomTask, Scruby, ScrubyModel
from scruby.aggregation import Counter

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


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


class TestCounter(CustomTask):
    """Test Counter."""

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


# Activate database.
Scruby.run()


async def test_task_counter() -> None:
    """Test a Counter class in custom task."""
    coll_user = Scruby(User)

    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await coll_user.add_doc(user)

    result = await coll_user.run_custom_task(
        custom_task=TestCounter(limit_docs=5),
    )
    assert len(result) == 5

    result = await coll_user.run_custom_task(
        custom_task=TestCounter(),
        filter_fn=lambda doc: doc.first_name == "John",
    )
    assert len(result) == 5
    #
    # Delete DB.
    Scruby.napalm()
