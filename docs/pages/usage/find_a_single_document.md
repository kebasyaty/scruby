#### Find a single document matching the filter

```py title="main.py" linenums="1"
"""Find a single document matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
Ideally, hundreds and even thousands of threads are required.
"""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants
from pprint import pprint as pp

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class User(BaseModel):
    """User model."""

    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime.datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def main() -> None:
    """Example."""
    # Get collection of `User`.
    user_coll = await Scruby.collection(User)

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    # Add user to collection.
    await user_coll.add_doc(user)

    # Find user by email.
    user_details: User | None = await user_coll.find_one(
        filter_fn=lambda doc: doc.email == "John_Smith@gmail.com",
    )
    if user_details is not None:
        pp(user_details)
    else:
        print("No User!")

    # Find user by birthday.
    user_details: User | None = await user_coll.find_one(
        filter_fn=lambda doc: doc.birthday == datetime.datetime(1970, 1, 1),
    )
    if user_details is not None:
        pp(user_details)
    else:
        print("No User!")

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
