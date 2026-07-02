#### Multiple inheritance

```py title="main.py" linenums="1"
"""Multiple inheritance."""

import anyio
from enum import StrEnum, auto
from typing import Annotated
from pydantic import Field
from scruby import Scruby, ScrubyModel
from pprint import pprint as pp


class CarType(StrEnum):
    """Car classification."""

    SEDAN = auto()
    LIFTBACK = auto()
    SUV = auto()
    HATCHBACK = auto()
    COUPE = "Coupe"
    CONVERTIBLE = auto()
    PICKUP = auto()
    MINIVAN = auto()


class MotorcycleType(StrEnum):
    """Motorcycle classification."""

    CRUISER = auto()
    SPORTBIKE = auto()
    NAKED = auto()
    TOURING = auto()
    SCOOTERS = auto()


class Vehicle(BaseModel):
    """Vehicle model."""

    brand: Annotated[str, Field(frozen=True)]
    model: Annotated[str, Field(frozen=True)]
    year: int
    power_reserve: int
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: f"{data['brand']}:{data['model']}",
        ),
    ]


class Car(ScrubyModel, Vehicle):
    """Car model."""

    type: Annotated[CarType, Field(title="Car classification")]


class Motorcycle(ScrubyModel, Vehicle):
    """Motorcycle model."""

    type: Annotated[MotorcycleType, Field(title="Motorcycle classification")]


async def main() -> None:
    """Example."""
    # Activate database
    Scruby.run()

    # Get collection `Car`
    car_coll = Scruby(Car)

    # Create car
    car = Car(
        brand="Mazda",
        model="EZ-6",
        year=2025,
        power_reserve=600,
        type=CarType.Liftback,
    )

    # Add car to collection
    await car_coll.add_doc(car)

    # Find car by model
    car_details: Car | None = car_coll.find_one(
        filter_fn=lambda doc: doc.model == "EZ-6",
    )

    # Print to console
    if car_details is not None:
        pp(car_details)
    else:
        print("No Car!")

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
