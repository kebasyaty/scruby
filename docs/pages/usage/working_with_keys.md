#### Working with keys

```py title="main.py" linenums="1"
"""Working with keys."""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel, ScrubySettings

ScrubySettings.db_root = "ScrubyDB"  # By default = "ScrubyDB"
ScrubySettings.hash_reduce_left = 6  # By default = 6
ScrubySettings.max_workers = None  # By default = None
ScrubySettings.plugins = []  # By default = []


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
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )
    # Add data of user to collection.
    await user_coll.add_doc(user)

    # Update data of  user to collection.
    await user_coll.update_doc(user)

    # Get user from collection.
    await user_coll.get_doc("+447986123456")  # => user
    await user_coll.get_doc("key missing")  # => KeyError

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
