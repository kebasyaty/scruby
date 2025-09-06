"""A fast key-value storage library.

Scruby is a fast key-value storage library that provides an ordered mapping from string keys to string values.
The library uses fractal-tree addressing.

The maximum size of the database is 16**32=340282366920938463463374607431768211456 branches,
each branch can store one or more keys.

The value of any key can be obtained in 32 steps, thereby achieving high performance.
There is no need to iterate through all the keys in search of the desired value.
"""

from __future__ import annotations

__all__ = (
    "Scruby",
    "constants",
)

from scruby import constants
from scruby.db import Scruby
