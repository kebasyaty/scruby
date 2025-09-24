"""A fast key-value storage library.

Scruby is a fast key-value storage asynchronous library that provides an
ordered mapping from string keys to string values.
The library uses fractal-tree addressing.

The database consists of collections.
The maximum size of the one collection is 16**8=4294967296 branches,
each branch can store one or more keys.

The value of any key in collection can be obtained in 8 steps,
thereby achieving high performance.

In the future, to search by value of key, the use of a quantum loop is supposed.
"""

from __future__ import annotations

__all__ = ("Scruby",)

import logging

from scruby.db import Scruby

logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
)
