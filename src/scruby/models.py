"""Models."""

from __future__ import annotations

__all__ = ("ScrubyModel",)


from datetime import datetime

from pydantic import BaseModel


class ScrubyModel(BaseModel):
    """A base class for creating Scruby models."""

    created_at: datetime | None = None
    updated_at: datetime | None = None


class CryptoModel(ScrubyModel):
    """Base class for creating password-enabled Scruby models.

    The bcrypt library is used to hash passwords.
    """
