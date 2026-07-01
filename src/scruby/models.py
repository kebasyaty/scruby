"""Scruby Models.

The module contains the following classes:

- `ScrubyModel` - A base class for creating Scruby models.
"""

from __future__ import annotations

__all__ = ("ScrubyModel",)


from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ScrubyModel(BaseModel):
    """A base class for creating Scruby models."""

    model_config = ConfigDict(strict=True)

    created_at: Annotated[
        datetime | None,
        Field(
            title="Created at",
            default=None,
        ),
    ]
    updated_at: Annotated[
        datetime | None,
        Field(
            title="Updated at",
            default=None,
        ),
    ]
