"""Asynchronous library for building and managing a hybrid database, by scheme of key-value.

The library uses fractal-tree addressing and
the search for documents based on the effect of a quantum loop.

The database consists of collections.
The maximum size of the one collection is 16**8=4294967296 branches,
each branch can store one or more keys.

The value of any key in collection can be obtained in 8 steps,
thereby achieving high performance.

The effectiveness of the search for documents based on a quantum loop,
requires a large number of processor threads.
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
