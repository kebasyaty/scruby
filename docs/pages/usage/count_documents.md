#### Get an estimate of number of documents using collection metadata

```py title="main.py" linenums="1"
"""Get an estimate of the number of documents in this collection using collection metadata."""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, settings

settings.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
settings.HASH_REDUCE_LEFT = 6  # By default = 6
settings.MAX_WORKERS = None  # By default = None


class User(BaseModel):
    """Model of User."""
    first_name: str
    last_name: str
    birthday: datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]
    # Extra fields
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def main() -> None:
    """Example."""
    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create user.
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    print(await user_coll.estimated_document_count())  # => 0

    # Add user to collection.
    await user_coll.add_doc(user)
    print(await user_coll.estimated_document_count())  # => 1

    # Delete user from collection.
    await user_coll.delete_key("+447986123456")
    print(await user_coll.estimated_document_count())  # => 0

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

#### Count number of documents in collection

```py title="main.py" linenums="1"
"""Count the number of documents a matching the filter in this collection."""

import anyio
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, settings

settings.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
settings.HASH_REDUCE_LEFT = 6  # By default = 6
settings.MAX_WORKERS = None  # By default = None


class User(BaseModel):
    """User model."""

    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # Extra fields
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def main() -> None:
    """Example."""
    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # Create users.
    for num in range(1, 10):
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, num),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
        )
        await db.set_key(user.key, user)

    result: int = await user_coll.count_documents(
        filter_fn=lambda doc: doc.email == "John_Smith_5@gmail.com" or doc.email == "John_Smith_8@gmail.com",
    )
    print(result:)  # => 2

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
