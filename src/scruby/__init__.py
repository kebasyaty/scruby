#                      _
#                     | |
#  ___  ___ _ __ _   _| |__  _   _
# / __|/ __| '__| | | | '_ \| | | |
# \__ \ (__| |  | |_| | |_) | |_| |
# |___/\___|_|   \__,_|_.__/ \__, |
#                             __/ |
#                            |___/
#
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
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
    "Scruby",
    "ScrubyModel",
    "ScrubyConfig",
)

from scruby.config import ScrubyConfig
from scruby.db import Scruby, ScrubyModel

ScrubyConfig.init_params()  # noqa: RUF067
