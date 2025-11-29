#### Find one or more documents matching the filter

```py title="main.py" linenums="1"
"""Find one or more documents matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
Ideally, hundreds and even thousands of threads are required.
"""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants
from pprint import pprint as pp

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

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, num),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.add_key(user.phone, user)

    # Find users by email.
    users: list[User] | None = user_coll.find_many(
        filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
    )
    if users is not None:
        pp(users)
    else:
        print("No users!")

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
