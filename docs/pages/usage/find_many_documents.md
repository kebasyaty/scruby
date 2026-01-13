#### Find many documents matching the filter

```py title="main.py" linenums="1"
"""Find many documents matching the filter.

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

    # Find cars by brand and year.
    car_list: list[Car] | None = await car_coll.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda" and doc.year == 2025,
    )
    if car_list is not None:
        pp(car_list)
    else:
        print("No cars!")

    # Find all cars.
    car_list: list[Car] | None = await car_coll.find_many()
    if car_list is not None:
        pp(car_list)
    else:
        print("No cars!")

    # For pagination output.
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
