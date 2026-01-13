#### Find a single document and delete

```py title="main.py" linenums="1"
"""Find a single document, matching the filter and delete it.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
"""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel, settings

settings.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
settings.HASH_REDUCE_LEFT = 6  # By default = 6
settings.MAX_WORKERS = None  # By default = None
settings.PLUGINS = []  # By default = []


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


async def main() -> None:
    """Example."""
    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    # Add user to collection.
    await user_coll.add_doc(user)

    # Find user by email.
    user_details: User | None = user_coll.find_one(
        filter_fn=lambda doc: doc.phone == "+447986123456",
    )
    # Delete user from collection.
    if user_details is not None:
        await user_coll.delete_doc(user_details.key)

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Find one or more documents and deletes

```py title="main.py" linenums="1"
"""Delete one or more documents matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
"""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel, settings

settings.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
settings.HASH_REDUCE_LEFT = 6  # By default = 6
settings.MAX_WORKERS = None  # By default = None
settings.PLUGINS = []  # By default = []


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

    amount_of_deleted: int = await user_coll.delete_many(
        filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
    )
    print(amount_of_deleted)  # => 2

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
