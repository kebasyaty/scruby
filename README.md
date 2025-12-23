<div align="center">
  <p align="center">
    <a href="https://github.com/kebasyaty/scruby">
      <img
        height="80"
        alt="Logo"
        src="https://raw.githubusercontent.com/kebasyaty/scruby/main/assets/logo.svg">
    </a>
  </p>
  <p>
    <h1>Scruby</h1>
    <h3>Asynchronous library for building and managing a hybrid database,<br>by scheme of key-value.</h3>
    <p align="center">
      <a href="https://github.com/kebasyaty/scruby/actions/workflows/test.yml" alt="Build Status"><img src="https://github.com/kebasyaty/scruby/actions/workflows/test.yml/badge.svg" alt="Build Status"></a>
      <a href="https://kebasyaty.github.io/scruby/" alt="Docs"><img src="https://img.shields.io/badge/docs-available-brightgreen.svg" alt="Docs"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI pyversions"><img src="https://img.shields.io/pypi/pyversions/scruby.svg" alt="PyPI pyversions"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI status"><img src="https://img.shields.io/pypi/status/scruby.svg" alt="PyPI status"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI version fury.io"><img src="https://badge.fury.io/py/scruby.svg" alt="PyPI version fury.io"></a>
      <br>
      <a href="https://pyrefly.org/" alt="Types: Pyrefly"><img src="https://img.shields.io/badge/types-Pyrefly-FFB74D.svg" alt="Types: Pyrefly"></a>
      <a href="https://docs.astral.sh/ruff/" alt="Code style: Ruff"><img src="https://img.shields.io/badge/code%20style-Ruff-FDD835.svg" alt="Code style: Ruff"></a>
      <a href="https://pypi.org/project/scruby"><img src="https://img.shields.io/pypi/format/scruby" alt="Format"></a>
      <a href="https://pepy.tech/projects/scruby"><img src="https://static.pepy.tech/badge/scruby" alt="PyPI Downloads"></a>
      <a href="https://github.com/kebasyaty/scruby/blob/main/LICENSE" alt="GitHub license"><img src="https://img.shields.io/github/license/kebasyaty/scruby" alt="GitHub license"></a>
    </p>
    <p align="center">
        The library uses fractal-tree addressing and
        <br>
        the search for documents based on the effect of a quantum loop.
        <br>
        The database consists of collections.
        <br>
        The maximum size of the one collection is <b>16**8=4294967296</b> branches,
        <br>
        each branch can store one or more keys.
        <br>
        The value of any key in collection can be obtained maximum in <b>8</b> steps,
        <br>
        thereby achieving high performance.
        <br>
        The effectiveness of the search for documents based on a quantum loop,
        <br>
        requires a large number of processor threads.
    </p>
  </p>
</div>

##

<br>

## Documentation

Online browsable documentation is available at [https://kebasyaty.github.io/scruby/](https://kebasyaty.github.io/scruby/ "Documentation").

## Requirements

[View the list of requirements](https://github.com/kebasyaty/scruby/blob/v0/REQUIREMENTS.md "Requirements").

## Installation

```shell
uv add scruby
```

## Usage

See more examples here [https://kebasyaty.github.io/scruby/latest/pages/usage/](https://kebasyaty.github.io/scruby/latest/pages/usage/ "Examples").

```python
"""Working with keys."""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, constants

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6

class User(BaseModel):
    """User model."""
    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime.datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def main() -> None:
    """Example."""
    # Get collection of `User`.
    user_coll = await Scruby.create(User)

    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    await user_coll.add_doc(user)

    await user_coll.update_doc(user)

    await user_coll.get_key("+447986123456")  # => user
    await user_coll.get_key("key missing")  # => KeyError

    await user_coll.has_key("+447986123456")  # => True
    await user_coll.has_key("key missing")  # => False

    await user_coll.delete_key("+447986123456")
    await user_coll.delete_key("+447986123456")  # => KeyError
    await user_coll.delete_key("key missing")  # => KeyError

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

```python
"""Find a single document matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
Ideally, hundreds and even thousands of threads are required.
"""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, Field
from scruby import Scruby, constants
from pprint import pprint as pp

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class Phone(BaseModel):
    """Phone model."""
    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    screen_diagonal: float = Field(strict=True)
    matrix_type: str = Field(strict=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


async def main() -> None:
    """Example."""
    # Get collection of `Phone`.
    phone_coll = await Scruby.create(Phone)

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

```python
"""Find one or more documents matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
Ideally, hundreds and even thousands of threads are required.
"""

import anyio
import datetime
from typing import Annotated
from pydantic import BaseModel, Field
from scruby import Scruby, constants
from pprint import pprint as pp

constants.DB_ROOT = "ScrubyDB"  # By default = "ScrubyDB"
constants.HASH_REDUCE_LEFT = 6  # By default = 6


class Car(BaseModel):
    """Car model."""
    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    year: int = Field(strict=True)
    power_reserve: int = Field(strict=True)
    # The key is always at the bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


async def main() -> None:
    """Example."""
    # Get collection of `Car`.
    car_coll = await Scruby.create(Car)

    # Create cars.
    for name in range(1, 10):
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

    # Get collection list.
    collection_list = await Scruby.collection_list()
    print(collection_list)  # ["Car"]

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

## Changelog

[View the change history](https://github.com/kebasyaty/scruby/blob/v0/CHANGELOG.md "Changelog").

## License

This project is licensed under the [MIT](https://github.com/kebasyaty/scruby/blob/main/LICENSE "MIT").
