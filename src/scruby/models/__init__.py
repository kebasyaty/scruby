# Scruby - Asynchronous library for building and managing a hybrid database, by scheme of key-value.
# Copyright (c) 2025 Gennady Kostyunin
# SPDX-License-Identifier: MIT
# SPDX-License-Identifier: GPL-3.0-or-later
"""Models."""

from __future__ import annotations

__all__ = (
    "ScrubyModel",
    "CryptModel",
)

from scruby.models.crypt_model import CryptModel
from scruby.models.scruby_model import ScrubyModel
