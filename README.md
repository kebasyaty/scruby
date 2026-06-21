<div align="center">
  <p align="center">
    <a href="https://github.com/kebasyaty/scruby">
      <img
        width="100%"
        alt="Logo"
        src="https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/logo.jpg">
    </a>
  </p>
  <p>
    <h1>Scruby (small shrub)</h1>
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
      <a href="https://github.com/kebasyaty/scruby/blob/main/MIT-LICENSE" alt="License: MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
      <a href="https://github.com/kebasyaty/scruby/blob/main/GPL-3.0-LICENSE" alt="License: GPL v3"><img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3"></a>
    </p>
    <p align="center">
      The library uses fractal-tree addressing and<br>
      the search for documents based on the effect of a quantum loop.
      <br>
      <br>
      The size of each collection is 16|256|4096|4294967296 branches,<br>
      each branch can store one or more keys.
      <br>
      <br>
      The value of any key in collection can be obtained in 1-8 steps,<br>
      thereby achieving high performance.
      <br>
      <br>
      The effectiveness of the search for documents based on a quantum loop,<br>
      requires a large number of processor threads.
    </p>
  </p>
</div>

##

<br>

<img src="https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/attention.svg" alt="Attention">
<p>
<b>Parameter `ScrubyConfig.HASH_REDUCE_LEFT - Scruby.run(hash_reduce_left = 7)`:</b>
<br>
7 = 16 branches in collection (is default) -> Docs: ~16000+, RAM: ~2G+, CPU: ~2+ (for development).
<br>
6 = 256 branches in collection -> Docs: ~256000+, RAM: ~4G+, CPU: ~2+ (for small projects).
<br>
5 = 4096 branches in collection -> Docs: ~4096000+, RAM: ~6G+, CPU: ~3+ (for large projects).
<br>
0 = 4294967296 branches in collection -> Docs: ~4,294967296×10¹²+, RAM: ~2G+, CPU: ~2+ (access only by keys).
<br>
<br>
<b>If you notice the production server slowing down,</b><br>
<b>you will need to add RAM and CPU.</b>
</p>

<br>
<br>
<br>

[![List of plugins](https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/links/plugins.svg "List of plugins")](https://github.com/kebasyaty/scruby/blob/v2/PLUGINS.md "List of plugins")

[![Documentation](https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/links/documentation.svg "Documentation")](https://kebasyaty.github.io/scruby/ "Documentation")

[![Requirements](https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/links/requirements.svg "Requirements")](https://github.com/kebasyaty/scruby/blob/v2/REQUIREMENTS.md "Requirements")

## Installation

```shell
uv add scruby
```

## Run

```shell
# Run Development:
uv run python main.py
# Run Production:
uv run python -OOP main.py
```

## Usage

[![Examples](https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/links/examples.svg "Examples")](https://kebasyaty.github.io/scruby/latest/pages/usage/ "Examples")

```python
"""Working with keys."""

import anyio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Annotated
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from scruby import Scruby, ScrubyModel, ScrubyConfig


class User(ScrubyModel):
    """User model."""
    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run()

    # Get/Create a User collection
    user_coll = Scruby(User)

    # Create user
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    # Add user to collection
    await user_coll.add_doc(user)

    # Update user data in a collection
    await user_coll.update_doc(user)

    # Get user details
    await user = user_coll.get_doc("+447986123456")
    await user_coll.get_doc("key missing")  # => None

    # Check for the presence of a key in the collection
    await user_coll.has_key("+447986123456")  # => True

    # Delete a document by key
    await user_coll.delete_doc("+447986123456")

    # Get collection name
    user_coll.collection_name()  # => User

    # Get collection list
    coll_list = Scruby.collection_list()  # => ["User"]

    # Get the number of documents in the collection from metadata
    await user_coll.estimated_document_count()  # => 1

    # Get the number of documents comparable to the filter
    user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 1

    # Clear collection
    Scruby.clear_collection("User")

    # Full database deletion
    # Hint: The main purpose is tests
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

```python
"""Find one document matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
"""

import anyio
from pydantic import Field
from scruby import ReturnType, Scruby, ScrubyConfig, ScrubyModel


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
    # Activate database.
    Scruby.run()

    # Get/Create a Phone collection
    phone_coll = Scruby(Phone)

    # Create phone
    phone = Phone(
        brand="Samsung",
        model="Galaxy A26",
        screen_diagonal=6.7,
        matrix_type="Super AMOLED",
    )

    # Add phone to collection
    await phone_coll.add_doc(phone)

    # Find phone by brand
    phone_details: Phone | None = phone_coll.find_one(
        filter_fn=lambda doc: doc.brand == "Samsung",
    )

    # Find phone by model
    phone_details: Phone | None = phone_coll.find_one(
        filter_fn=lambda doc: doc.model == "Galaxy A26",
    )

    # Return phone in JSON format
    phone_details: str | None = phone_coll.find_one(
        filter_fn=lambda doc: doc.model == "Galaxy A26",
        return_type=ReturnType.JSON,
    )

    # Return phone in Dictionary format
    phone_details: dict | None = phone_coll.find_one(
        filter_fn=lambda doc: doc.model == "Galaxy A26",
        return_type=ReturnType.DICT,
    )

    # Full database deletion
    # Hint: The main purpose is tests
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

```python
"""Find many documents matching the filter.

The search is based on the effect of a quantum loop.
The search effectiveness depends on the number of processor threads.
"""

import anyio
from typing import Annotated
from pydantic import Field
from scruby import ReturnType, Scruby, ScrubyConfig, ScrubyModel


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
    # Activate database.
    Scruby.run()

    # Get/Create a Car collection
    car_coll = Scruby(Car)

    # Create cars
    for num in range(1, 10):
        car = Car(
            brand="Mazda",
            model=f"EZ-6 {num}",
            year=2025,
            power_reserve=600,
        )
        await car_coll.add_doc(car)

    # Find all cars
    car_list: list[Car] | None = car_coll.find_many()

    # Find cars by brand and year
    car_list: list[Car] | None = car_coll.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda" and doc.year == 2025,
    )

    # Pagination
    car_list: list[Car] | None = car_coll.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda",
        limit_docs=5,
        page_number=2,
    )

    # Sorting
    car_list: list[Car] | None = car_coll.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda",
        sort_fn=lambda doc: (doc.brand, doc.updated_at),
        sort_reverse=True,
    )

    # Return cars in JSON format
    car_list: str | None = car_coll.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda",
        return_type=ReturnType.JSON,
    )

    # Return cars in Dictionary format
    car_list: list[dict] | None = car_coll.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda",
        return_type=ReturnType.DICT,
    )

    # Update one or more documents matching the filter
    count_updated = await car_coll.update_many(
        new_data={"brand": "BMW"},
        filter_fn=lambda doc: doc.brand == "Mazda",
    )

    # Delete one or more documents matching the filter
    count_deleted = await car_coll.delete_many(
        filter_fn=lambda doc: doc.brand == "BMW",
    )

    # Full database deletion
    # Hint: The main purpose is tests
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

<br>

[![Changelog](https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/links/changelog.svg "Changelog")](https://github.com/kebasyaty/scruby/blob/v2/CHANGELOG.md "Changelog")

[![MIT](https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/links/mit.svg "MIT")](https://github.com/kebasyaty/scruby/blob/main/MIT-LICENSE "MIT")

[![GPL-3.0](https://raw.githubusercontent.com/kebasyaty/scruby/v2/assets/links/gpl-3.0-or-later.svg "GPL-3.0")](https://github.com/kebasyaty/scruby/blob/main/GPL-3.0-LICENSE "GPL-3.0")
