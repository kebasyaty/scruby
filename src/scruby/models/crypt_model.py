"""Crypt Model.

For operations with passwords in Scruby models.
"""

from __future__ import annotations

__all__ = ("CryptModel",)


from typing import Annotated

import bcrypt
from pydantic import BaseModel, Field, SecretStr


class CryptModel(BaseModel):
    """Add password support to the Scruby model.

    The bcrypt library is used to hash passwords.
    To operations with a password, use only special methods.
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
        """Takes the raw password string and converts it into a hash.

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
        """Converts the raw password to a hash and adds it to the password field.

        Uses the bcrypt library.

        Args:
            password (str | SecretStr): User password.

        Returns:
            None

        Raises:
            ValueError: If the password already exists.
        """
        assert isinstance(password, (str, SecretStr)), "Valid type: str | SecretStr."
        #
        # Throw an exception if the password is present
        if bool(self.password):
            msg = "The password already exists. To update it, use the `update_password` method."
            raise ValueError(msg)
        #
        hashed_password = self.hash_raw_password(password)
        # Set user password.
        # Hint: To temporarily bypass the `frozen=True` limitation.
        object.__setattr__(self, "password", hashed_password)  # ruff:ignore[unnecessary-dunder-call]

    def password_is_valid(self, password: str | SecretStr) -> bool:
        """Check password validity.

        Takes some password and matches it with an existing one.
        Can be used to verify a login attempt.

        Args:
            password (str | SecretStr): User password.

        Returns:
            True if the passwords are the same and False if they are not the same.
        """
        assert isinstance(password, (str, SecretStr)), "Valid type: str | SecretStr."
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
        if __debug__:
            if not isinstance(old_password, (str, SecretStr)):
                msg = "Argument: `old_password` => Valid type: str | SecretStr."
                raise AssertionError(msg)
            if not isinstance(new_password, (str, SecretStr)):
                msg = "Argument: `new_password` => Valid type: str | SecretStr."
                raise AssertionError(msg)
        #
        # Throw an exception if the current password is missing
        if not bool(self.password):
            msg = "The current password cannot be updated because it is missing."
            raise ValueError(msg)
        # Throw an exception if the old password does not match the current one
        if not self.password_is_valid(old_password):
            raise ValueError("Old password doesn't match.")
        # Pre-reset the password to default state.
        # Hint: To temporarily bypass the `frozen=True` limitation.
        object.__setattr__(self, "password", None)  # ruff:ignore[unnecessary-dunder-call]
        # Replace the current password with a new one
        self.set_password(new_password)
