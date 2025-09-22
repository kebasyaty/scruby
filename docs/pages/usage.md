#### Working with keys

```py title="main.py" linenums="1"
import anyio
import datetime
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from scruby import Scruby, constants

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"

class User(BaseModel):
    """Model of User."""
    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: PhoneNumber

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

#### Find a single document

```py title="main.py" linenums="1"
"""Find a single document.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
Ideally, hundreds and even thousands of streams are required.
"""

import anyio
import datetime
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from scruby import Scruby, constants
from pprint import pprint as pp

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.LENGTH_REDUCTION_HASH = 6  # 256 keys (main purpose is tests).

class User(BaseModel):
    """Model of User."""
    first_name: str
    last_name: str
    birthday: datetime.datetime
    email: EmailStr
    phone: PhoneNumber

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
    if user_details is not None:
        pp(user_details)
    else:
        print("No User!")

    # Find user by birthday.
    user_details: User | None = user_coll.find_one(
        filter_fn=lambda doc: doc.birthday == datetime.datetime(1970, 1, 1),
    )
    if user_details is not None:
        pp(user_details)
    else:
        print("No User!")

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()

if __name__ == "__main__":
    anyio.run(main)
```
