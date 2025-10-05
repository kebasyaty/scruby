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
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # 256 branches in collection
                                # (main purpose is tests).


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
    user_coll = Scruby(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            age=f"{num * 10}",
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.set_key(f"+44798612345{num}", user)

    number_updated_users = user_coll.update_many(
        filter_fn=lambda _: True,  # Update all documents.
        new_data={"first_name": "Georg"},
    )
    print(number_updated_users)  # => 9

    users: list[User] | None = user_coll.find_many(
        filter_fn=lambda _: True,  # Find all documents
    )
    for user in users:
        print(user.first_name)  # => Georg

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
