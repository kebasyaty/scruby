#### Update documents

```py title="main.py" linenums="1"
"""Update one or more documents matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
"""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel


class User(ScrubyModel):
    """User model."""
    first_name: str
    last_name: str
    birthday: datetime
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
            last_name="Smith",
            birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await db.add_doc(user)

    number_updated_users = await user_coll.update_many(
        new_data={"first_name": "Georg"},
    )
    print(number_updated_users)  # => 9

    users: list[User] | None = user_coll.find_many()
    for user in users:
        print(user.first_name)  # => Georg

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
