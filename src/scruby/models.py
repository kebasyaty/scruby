"""Model."""

from __future__ import annotations

__all__ = ("ScrubyModel",)


from datetime import datetime

from pydantic import BaseModel


class ScrubyModel(BaseModel):
    """Additional fields for models."""

    created_at: datetime | None = None
    updated_at: datetime | None = None
