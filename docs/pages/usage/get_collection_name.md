#### Get collection name

```py title="main.py" linenums="1"
"""Get collection name."""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """Model of User."""
    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


async def main() -> None:
    """Example."""
    # Get collection of `User`.
    user_coll = await Scruby.create(User)

    print(user_coll.collection_name())  # "User"

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
