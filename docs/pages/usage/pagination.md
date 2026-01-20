#### Pagination documents matching the filter

```py title="main.py" linenums="1"
"""Pagination documents matching the filter.

Pagination is used to separate long sets of data so
that it is easier for a user to consume information.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
"""

import anyio
from typing import Annotated
from pydantic import Field
from scruby import Scruby, ScrubyModel, ScrubySettings
from pprint import pprint as pp

ScrubySettings.db_root = "ScrubyDB"  # By default = "ScrubyDB"
ScrubySettings.hash_reduce_left = 6  # By default = 6
ScrubySettings.max_workers = None  # By default = None
ScrubySettings.plugins = []  # By default = []


class Car(ScrubyModel):
    """Car model."""
    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    year: int = Field(strict=True)
    power_reserve: int = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


async def main() -> None:
    """Example."""
    # Get collection `Car`.
    car_coll = await Scruby.collection(Car)

    # Create cars.
    for num in range(1, 10):
        car = Car(
            brand="Mazda",
            model=f"EZ-6 {num}",
            year=2025,
            power_reserve=600,
        )
        await car_coll.add_doc(car)

    # Pagination.
    car_list: list[Car] | None = await car_coll.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda",
        limit_docs=5,
        page_number=2,
    )
    if car_list is not None:
        pp(car_list)
    else:
        print("No cars!")

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
