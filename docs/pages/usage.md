```python
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
    db = Scruby(User)

    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    await db.set_key("+447986123456", user)

    await db.get_key("+447986123456")  # => user
    await db.get_key("key missing")  # => KeyError

    await db.has_key("+447986123456")  # => True
    await db.has_key("key missing")  # => False

    await db.delete_key("+447986123456")
    await db.delete_key("+447986123456")  # => KeyError
    await db.delete_key("key missing")  # => KeyError

    # Full database deletion.
    # Hint: The main purpose is tests.
    await db.napalm()
    await db.napalm()  # => FileNotFoundError


if __name__ == "__main__":
    anyio.run(main)
```
