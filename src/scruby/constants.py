"""Constant variables.

The module contains the following variables:

- `DB_ROOT` - Path to root directory of database. `By default = "ScrubyDB"` (*in root of project*).
- `LENGTH_REDUCTION_HASH` - The length of the hash reduction on the left side.
    - `0` - 4294967296 keys (by default).
    - `2` - 16777216 keys.
    - `4` - 65536 keys.
    - `6` - 256 keys (main purpose is tests).
"""

from __future__ import annotations

__all__ = (
    "DB_ROOT",
    "LENGTH_REDUCTION_HASH",
)

from typing import Literal

# Path to root directory of database
# By default = "ScrubyDB" (in root of project).
DB_ROOT: str = "ScrubyDB"

# The length of the hash reduction on the left side.
# 0 = 4294967296 keys (by default).
# 2 = 16777216 keys.
# 4 = 65536 keys.
# 6 = 256 keys (main purpose is tests).
LENGTH_REDUCTION_HASH: Literal[0, 2, 4, 6] = 0
