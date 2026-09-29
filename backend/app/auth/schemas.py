from pydantic import Field

from app.validation.common import NEXXABaseModel


class PasswordCredentials(NEXXABaseModel):
    """Validated password credentials."""

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class AuthenticatedUser(NEXXABaseModel):
    """Minimal authenticated-user representation."""

    user_id: int