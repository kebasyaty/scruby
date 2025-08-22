```python
import anyio
from scruby import Scruby


async def main() -> None:
    """Example."""

    db = Scruby()
    await db.set_key("key name", "Some text")
    await db.get_key("key name")  # => "Some text"
    await db.get_key("key missing")  # => KeyError
    await db.has_key("key name")  # => True
    await db.has_key("key missing")  # => False
    await db.delete_key("key name")
    await db.delete_key("key missing")  # => KeyError
    # Full database deletion.
    await db.napalm()
    await db.napalm()  # => FileNotFoundError


if __name__ == "__main__":
    anyio.run(main)
```
