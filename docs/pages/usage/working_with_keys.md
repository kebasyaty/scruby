#### Working with keys

```py title="main.py" linenums="1"
"""Working with keys."""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel
from pprint import pprint as pp


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

    # Create/get the `User` collection.
    user_coll = Scruby(User)

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )
    # Add data of user to collection.
    await user_coll.add_doc(user)

    # Update data of  user to collection.
    await user_coll.update_doc(user)

    # Get user details
    user = await user_coll.get_doc("+447986123456")
    pp(user)
    await user_coll.get_doc("key missing")  # => None

    await user_coll.has_key("+447986123456")  # => True
    await user_coll.has_key("key missing")  # => False

    await user_coll.delete_doc("+447986123456")
    await user_coll.delete_doc("+447986123456")  # => KeyError
    await user_coll.delete_doc("key missing")  # => KeyError

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
