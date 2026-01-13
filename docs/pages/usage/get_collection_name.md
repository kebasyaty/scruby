#### Get collection name

```py title="main.py" linenums="1"
"""Get collection name."""

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

    print(user_coll.collection_name())  # "User"

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
