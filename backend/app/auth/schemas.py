from pydantic import EmailStr, Field

from app.validation.common import NEXXABaseModel


class PasswordCredentials(NEXXABaseModel):
    """Validated password credentials."""

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserCreate(NEXXABaseModel):
    """Validated data required to create a user."""

    email: EmailStr

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(NEXXABaseModel):
    """Safe API representation of a user."""

    id: int
    email: EmailStr
    username: str | None
    is_active: bool


class AuthenticatedUser(NEXXABaseModel):
    """Minimal authenticated-user representation."""

    user_id: int