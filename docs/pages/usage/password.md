#### Operations with passwords

```py title="main.py" linenums="1"
"""Operations with passwords.

To operations with a password, use only special methods.
Do not use this field directly.
"""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import CryptModel, Scruby, ScrubyModel


class User(ScrubyModel, CryptModel):
    """User model."""

    username: str
    first_name: str
    last_name: str
    birthday: datetime
    email: EmailStr
    phone: Annotated[
        PhoneNumber,
        PhoneNumberValidator(number_format="E164"),
        Field(strict=False),
    ]
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["username"],
        ),
    ]


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run()

    # Create/get the `User` collection.
    user_coll = Scruby(User)

    # Create user
    user = User(
        username="user_1",
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    test_pass = "user_pass_123"

    # Add user password
    user.set_password(test_pass)

    # Add user to collection
    await user_coll.add_doc(user)

    # Get user details
    user_details = await user_coll.get_doc("user_1")

    # Check a password
    user_details.password_is_valid(test_pass)  # True

    # Update existing password
    user_details.update_password(test_pass, new_test_pass)

    # Update user data in a collection
    await user_coll.update_doc(user_details)

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
