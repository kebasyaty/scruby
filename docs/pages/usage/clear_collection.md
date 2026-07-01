#### Clear Collection

```py title="main.py" linenums="1"
"""Clear collection."""

import anyio
from datetime import datetime
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

    collection_list = Scruby.collection_list()
    print(ucollection_list)  # ["User"]

    Scruby.clear_collection("User")

    collection_list = Scruby.collection_list()
    print(ucollection_list)  # None

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
