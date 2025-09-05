```python
import anyio
import datetime
from pydantic import BaseModel
from scruby import Scruby


async def main() -> None:
    """Example."""

  class User(BaseModel):
      """User model."""

      first_name: str
      last_name: str
      birthday: datetime.datetime
      email: str
      phone: str


    db = Scruby(
        class_model=User,
        db_name="ScrubyDB",  # By default = "ScrubyDB"
    )

    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),  # noqa: DTZ001
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
    await db.napalm()
    await db.napalm()  # => FileNotFoundError


if __name__ == "__main__":
    anyio.run(main)
```
