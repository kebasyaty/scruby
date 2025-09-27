#### Find a single document and delete

```py title="main.py" linenums="1"
"""Finds one or more documents matching the filter and deletes their.

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

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    # Add user to collection.
    await user_coll.set_key("+447986123456", user)

    # Find user by email.
    user_details: User | None = user_coll.find_one(
        filter_fn=lambda doc: doc.email == "John_Smith@gmail.com",
    )
    # Delete user from collection.
    await user_coll.delete_key(user_details.phone)

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Find one or more documents and deletes

```py title="main.py" linenums="1"
"""Find one or more documents matching the filter and deletes their.

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
            last_name="Smith",
            birthday=datetime.datetime(1970, 1, num),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await user_coll.set_key(f"+44798612345{num}", user)

    amount_of_deleted: int = user_coll.find_many_and_delete(
        filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
    )
    print(amount_of_deleted)  # => 2

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
