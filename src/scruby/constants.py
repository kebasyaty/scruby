"""Constant variables.

The module contains the following variables:

- `DB_ROOT` - Path to root directory of database. `By default = "ScrubyDB"` (*in root of project*).
- `LENGTH_SEPARATED_HASH` - Length of separated hash for create path inside collection.
    - `2` - 256 keys (main purpose is tests).
    - `4` - 65536 keys.
    - `6` - 16777216 keys.
    - `8` - 4294967296 keys (by default).
"""

from __future__ import annotations

__all__ = (
    "DB_ROOT",
    "LENGTH_SEPARATED_HASH",
)

from typing import Literal

# Path to root directory of database
# By default = "ScrubyDB" (in root of project).
DB_ROOT: str = "ScrubyDB"

# Length of separated hash for create path inside collection.
# By default = 8
# 2 = 256 keys (main purpose is tests).
# 4 = 65536 keys.
# 6 = 16777216 keys.
# 8 = 4294967296 keys (by default).
LENGTH_SEPARATED_HASH: Literal[2, 4, 6, 8] = 8
