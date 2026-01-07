#
# .dP"Y8  dP""b8 88""Yb 88   88 88""Yb Yb  dP
# `Ybo." dP   `" 88__dP 88   88 88__dP  YbdP
# o.`Y8b Yb      88"Yb  Y8   8P 88""Yb   8P
# 8bodP'  YboodP 88  Yb `YbodP' 88oodP  dP
#
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
#
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

__all__ = (
    "settings",
    "Scruby",
    "ScrubyModel",
)

from scruby import settings
from scruby.db import Scruby, ScrubyModel
