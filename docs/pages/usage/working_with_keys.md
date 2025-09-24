```py title="main.py" linenums="1"
"""Working with keys."""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"

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

    # Get user from collection.
    await user_coll.get_key("+447986123456")  # => user
    await user_coll.get_key("key missing")  # => KeyError

    await user_coll.has_key("+447986123456")  # => True
    await user_coll.has_key("key missing")  # => False

    await user_coll.delete_key("+447986123456")
    await user_coll.delete_key("+447986123456")  # => KeyError
    await user_coll.delete_key("key missing")  # => KeyError

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()

if __name__ == "__main__":
    anyio.run(main)
```
