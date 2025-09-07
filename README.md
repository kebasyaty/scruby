<div align="center">
  <p align="center">
    <a href="https://github.com/kebasyaty/scruby">
      <img
        height="90"
        alt="Logo"
        src="https://raw.githubusercontent.com/kebasyaty/scruby/main/assets/logo.svg">
    </a>
  </p>
  <p>
    <h1>Scruby</h1>
    <h3>A fast key-value storage library.</h3>
    <p align="center">
      <a href="https://github.com/kebasyaty/scruby/actions/workflows/test.yml" alt="Build Status"><img src="https://github.com/kebasyaty/scruby/actions/workflows/test.yml/badge.svg" alt="Build Status"></a>
      <a href="https://kebasyaty.github.io/scruby/" alt="Docs"><img src="https://img.shields.io/badge/docs-available-brightgreen.svg" alt="Docs"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI pyversions"><img src="https://img.shields.io/pypi/pyversions/scruby.svg" alt="PyPI pyversions"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI status"><img src="https://img.shields.io/pypi/status/scruby.svg" alt="PyPI status"></a>
      <a href="https://pypi.python.org/pypi/scruby/" alt="PyPI version fury.io"><img src="https://badge.fury.io/py/scruby.svg" alt="PyPI version fury.io"></a>
      <br>
      <a href="https://github.com/kebasyaty/scruby/issues"><img src="https://img.shields.io/github/issues/kebasyaty/scruby.svg" alt="GitHub issues"></a>
      <a href="https://pepy.tech/projects/scruby"><img src="https://static.pepy.tech/badge/scruby" alt="PyPI Downloads"></a>
      <a href="https://github.com/kebasyaty/scruby/blob/main/LICENSE" alt="GitHub license"><img src="https://img.shields.io/github/license/kebasyaty/scruby" alt="GitHub license"></a>
      <a href="https://mypy-lang.org/" alt="Types: Mypy"><img src="https://img.shields.io/badge/types-Mypy-202235.svg?color=0c7ebf" alt="Types: Mypy"></a>
      <a href="https://docs.astral.sh/ruff/" alt="Code style: Ruff"><img src="https://img.shields.io/badge/code%20style-Ruff-FDD835.svg" alt="Code style: Ruff"></a>
      <a href="https://github.com/kebasyaty/scruby" alt="PyPI implementation"><img src="https://img.shields.io/pypi/implementation/scruby" alt="PyPI implementation"></a>
      <br>
      <a href="https://pypi.org/project/scruby"><img src="https://img.shields.io/pypi/format/scruby" alt="Format"></a>
      <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/languages/top/kebasyaty/scruby" alt="Top"></a>
      <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/repo-size/kebasyaty/scruby" alt="Size"></a>
      <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/last-commit/kebasyaty/scruby/main" alt="Last commit"></a>
      <a href="https://github.com/kebasyaty/scruby/releases/" alt="GitHub release"><img src="https://img.shields.io/github/release/kebasyaty/scruby" alt="GitHub release"></a>
    </p>
    <p align="center">
      Scruby is a fast key-value storage library that provides an ordered mapping from string keys to string values.
      The library uses fractal-tree addressing.
      <br>
      The database consists of collections.
      The maximum size of the one collection is 16**8=4294967296 branches,
      each branch can store one or more keys.
      <br>
      The value of any key in collection can be obtained in 8 steps, thereby achieving high performance.
      <br>
      In the future, to search by value of key, the use of a quantum loop is supposed.
    </p>
  </p>
</div>

## Documentation

Online browsable documentation is available at [https://kebasyaty.github.io/scruby/](https://kebasyaty.github.io/scruby/ "Documentation").

## Requirements

[View the list of requirements](https://github.com/kebasyaty/scruby/blob/v0/REQUIREMENTS.md "Requirements").

## Installation

```shell
uv add scruby
```

## Usage

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
    # Get collection of `User`.
    user_coll = Scruby(User)

    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime.datetime(1970, 1, 1),
        email="John_Smith@gmail.com",
        phone="+447986123456",
    )

    await user_coll.set_key("+447986123456", user)

    await user_coll.get_key("+447986123456")  # => user
    await user_coll.get_key("key missing")  # => KeyError

    await user_coll.has_key("+447986123456")  # => True
    await user_coll.has_key("key missing")  # => False

    await user_coll.delete_key("+447986123456")
    await user_coll.delete_key("+447986123456")  # => KeyError
    await user_coll.delete_key("key missing")  # => KeyError

    # Full database deletion.
    # Hint: The main purpose is tests.
    await Scruby.napalm()

if __name__ == "__main__":
    anyio.run(main)
```

## Changelog

[View the change history](https://github.com/kebasyaty/scruby/blob/v0/CHANGELOG.md "Changelog").

## License

This project is licensed under the [MIT](https://github.com/kebasyaty/scruby/blob/main/LICENSE "MIT").
