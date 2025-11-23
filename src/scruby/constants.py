"""Constant variables.

The module contains the following variables:

- `DB_ROOT` - Path to root directory of database. `By default = "ScrubyDB" (in root of project)`.
- `HASH_REDUCE_LEFT` - The length of the hash reduction on the left side.
    - `0` - 4294967296 branches in collection.
    - `2` - 16777216 branches in collection.
    - `4` - 65536 branches in collection.
    - `6` - 256 branches in collection (by default).
"""

from __future__ import annotations

__all__ = (
    "DB_ROOT",
    "HASH_REDUCE_LEFT",
)

from typing import Literal

# Path to root directory of database
# By default = "ScrubyDB" (in root of project).
DB_ROOT: str = "ScrubyDB"

# The length of the hash reduction on the left side.
# 0 = 4294967296 branches in collection.
# 2 = 16777216 branches in collection.
# 4 = 65536 branches in collection.
# 6 = 256 branches in collection (by default).
# Number of branches is number of requests to the hard disk during quantum operations.
# Quantum operations: find_one, find_many, count_documents, delete_many, run_custom_task.
HASH_REDUCE_LEFT: Literal[0, 2, 4, 6] = 6
