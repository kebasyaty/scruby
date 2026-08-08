"""Test a Max class in custom task."""

from __future__ import annotations

from typing import Annotated, Any

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CustomTask, Scruby, ScrubyModel
from scruby.aggregation import Max

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


# Activate database.
Scruby.run()


async def test_task_calculate_max() -> None:
    """Test a Max class in custom task."""
    user_coll = Scruby(User)

    for num in range(1, 10):
        user = User(
            first_name="John",
            age=int(f"{num * 10}"),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_doc(user)

    result = await user_coll.run_custom_task(CalculateMaxAgeUsers())
    assert result == pytest.approx(90.0)
    #
    # Delete DB.
    Scruby.napalm()
