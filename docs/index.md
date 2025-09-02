<div align="center">
  <p align="center">
    <a href="https://github.com/kebasyaty/scruby">
      <img
        height="150"
        alt="Logo"
        src="https://raw.githubusercontent.com/kebasyaty/scruby/main/assets/logo.svg">
    </a>
  </p>
  <br>
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
    <a href="https://docs.astral.sh/ruff/" alt="Code style: Ruff"><img src="https://img.shields.io/badge/code%20style-Ruff-FDD835.svg" alt="Code style: Ruff"></a>
    <a href="https://github.com/kebasyaty/scruby" alt="PyPI implementation"><img src="https://img.shields.io/pypi/implementation/scruby" alt="PyPI implementation"></a>
    <br>
    <a href="https://pypi.org/project/scruby"><img src="https://img.shields.io/pypi/format/scruby" alt="Format"></a>
    <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/languages/top/kebasyaty/scruby" alt="Top"></a>
    <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/repo-size/kebasyaty/scruby" alt="Size"></a>
    <a href="https://github.com/kebasyaty/scruby"><img src="https://img.shields.io/github/last-commit/kebasyaty/scruby/main" alt="Last commit"></a>
    <a href="https://github.com/kebasyaty/scruby/releases/" alt="GitHub release"><img src="https://img.shields.io/github/release/kebasyaty/scruby" alt="GitHub release"></a>
  </p>
</div>

<hr>

::: scruby
    options:
      members: no

<hr>

#### Installation

```shell
uv add scruby
```

#### Usage

```python
import anyio
from scruby import Scruby


async def main() -> None:
    """Example."""

    db = Scruby()
    await db.set_key("key name", "Some text")
    # Update key
    await db.set_key("key name", "Some new text")

    user_details = {
        "first name": "John",
        "last name": "Smith",
        "email": "John_Smith@gmail.com",
        "phone": "+447986123456",
    }
    await db.set_key("+447986123456", user_details)

    await db.get_key("key name")  # => "Some text"
    await db.get_key("key missing")  # => KeyError

    await db.has_key("key name")  # => True
    await db.has_key("key missing")  # => False

    await db.delete_key("key name")
    await db.delete_key("key name")  # => KeyError
    await db.delete_key("key missing")  # => KeyError

    # Full database deletion.
    await db.napalm()
    await db.napalm()  # => FileNotFoundError


if __name__ == "__main__":
    anyio.run(main)
```

#### Requirements

[View the list of requirements.](https://github.com/kebasyaty/scruby/blob/main/REQUIREMENTS.md "View the list of requirements.")

#### Changelog

[View the change history.](https://github.com/kebasyaty/scruby/blob/main/CHANGELOG.md "Changelog")

#### License

_This project is licensed under the_ [MIT](https://github.com/kebasyaty/scruby/blob/main/LICENSE "MIT").
