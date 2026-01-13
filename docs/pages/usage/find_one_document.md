#### Find one document matching the filter

```py title="main.py" linenums="1"
"""Find one document matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
"""

import anyio
from typing import Annotated
from pydantic import Field
from scruby import Scruby, ScrubyModel, settings
from pprint import pprint as pp

settings.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
settings.HASH_REDUCE_LEFT = 6  # By default = 6
settings.MAX_WORKERS = None  # By default = None
settings.PLUGINS = []  # By default = []


class Phone(ScrubyModel):
    """Phone model."""
    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    screen_diagonal: float = Field(strict=True)
    matrix_type: str = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


async def main() -> None:
    """Example."""
    # Get collection `Phone`.
    phone_coll = await Scruby.collection(Phone)

    # Create phone.
    phone = Phone(
        brand="Samsung",
        model="Galaxy A26",
        screen_diagonal=6.7,
        matrix_type="Super AMOLED",
    )

    # Add phone to collection.
    await phone_coll.add_doc(phone)

    # Find phone by brand.
    phone_details: Phone | None = await phone_coll.find_one(
        filter_fn=lambda doc: doc.brand == "Samsung",
    )
    if phone_details is not None:
        pp(phone_details)
    else:
        print("No Phone!")

    # Find phone by model.
    phone_details: Phone | None = await phone_coll.find_one(
        filter_fn=lambda doc: doc.model == "Galaxy A26",
    )
    if phone_details is not None:
        pp(phone_details)
    else:
        print("No Phone!")

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
