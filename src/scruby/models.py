"""Scruby Models.

The module contains the following classes:

- `ScrubyModel` - A base class for creating Scruby models.
- `CryptModel` - Add password support to the Scruby model.
"""

from __future__ import annotations

__all__ = ("ScrubyModel",)


from datetime import datetime
from typing import Annotated

import bcrypt
from pydantic import BaseModel, ConfigDict, Field, SecretStr


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


class CryptModel(BaseModel):
    """Add password support to the Scruby model.

    The bcrypt library is used to hash passwords.
    To work with a password, use only special methods.
    Do not use this field directly.
    """

    password: Annotated[
        str | None,
        Field(
            title="Password",
            frozen=True,
            default=None,
            min_length=8,
            max_length=256,
        ),
    ]

    def hash_raw_password(self, password: str | SecretStr) -> str:
        """Takes a string and converts it to a hash.

        Uses the bcrypt library.

        Args:
            password (str | SecretStr): User password.

        Returns:
            Secure hash string.
        """
        # Extract the plain text string regardless of input format
        plain_password = password.get_secret_value() if isinstance(password, SecretStr) else password
        # Securely hash using bcrypt
        password_bytes = plain_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        # Return the decoded hash string
        return hashed_bytes.decode("utf-8")

    def set_password(self, password: str | SecretStr) -> None:
        """Converts the value to a hash and adds it to the password field.

        Uses the bcrypt library.

        Args:
            password (str | SecretStr): User password.

        Returns:
            None
        """
        assert isinstance(password, (str, SecretStr)), "Valid type: str | SecretStr"
        #
        hashed_password = self.hash_raw_password(password)
        # To temporarily bypass the `frozen=True` limitation
        object.__setattr__(self, "password", hashed_password)  # noqa: PLC2801

    def password_is_valid(self, password: str | SecretStr) -> bool:
        """Check password validity.

        Takes some password and matches it with an existing one.
        Can be used to verify a login attempt.

        Args:
            password (str | SecretStr): User password.

        Returns:
            True if the passwords are the same and False if they are not the same.
        """
        assert isinstance(password, (str, SecretStr)), "Valid type: str | SecretStr"
        #
        if not bool(self.password):
            return False
        #
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def update_password(
        self,
        old_password: str | SecretStr,
        new_password: str | SecretStr,
    ) -> None:
        """Update existing password.

        Args:
            old_password (str | SecretStr): Old user password.
            new_password (str | SecretStr): New user password.

        Returns:
            None

        Raises:
            ValueError: If the current password cannot be updated because it is missing.
            ValueError: If the old password does not match the current one.
        """
        assert isinstance(old_password, (str, SecretStr)), "Valid type: str | SecretStr"
        assert isinstance(new_password, (str, SecretStr)), "Valid type: str | SecretStr"
        #
        # Throw an exception if the current password is missing
        if self.password is None:
            msg = "The current password cannot be updated because it is missing"
            raise ValueError(msg)
        # Throw an exception if the old password does not match the current one
        if not self.password_is_valid(old_password):
            raise ValueError("Old password doesn't match")
        # Replace the current password with a new one
        self.set_password(new_password)
