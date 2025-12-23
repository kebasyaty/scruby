#### Update documents

```py title="main.py" linenums="1"
"""Update one or more documents matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
Ideally, hundreds and even thousands of threads are required.
"""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """User model."""

    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime.datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def main() -> None:
    """Example."""
    # Get collection of `User`.
    user_coll = await Scruby.create(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=f"{num * 10}",
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_key(user.key, user)

    number_updated_users = await user_coll.update_many(
        filter_fn=lambda _: True,  # Update all documents.
        new_data={"first_name": "Georg"},
    )
    print(number_updated_users)  # => 9

    users: list[User] | None = await user_coll.find_many(
        filter_fn=lambda _: True,  # Find all documents
    )
    for user in users:
        print(user.first_name)  # => Georg

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
