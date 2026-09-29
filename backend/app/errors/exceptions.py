class NEXXAError(Exception):
    """Base exception for expected NEXXA application errors."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class NotFoundError(NEXXAError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found.",
    ) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=message,
        )


class ValidationError(NEXXAError):
    """Raised when application-level validation fails."""

    def __init__(
        self,
        message: str = "Validation failed.",
    ) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
        )


class AuthenticationError(NEXXAError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication required.",
    ) -> None:
        super().__init__(
            code="AUTHENTICATION_REQUIRED",
            message=message,
        )


class AuthorizationError(NEXXAError):
    """Raised when the authenticated user lacks permission."""

    def __init__(
        self,
        message: str = (
            "You are not authorized to access this resource."
        ),
    ) -> None:
        super().__init__(
            code="FORBIDDEN",
            message=message,
        )


class ProviderUnavailableError(NEXXAError):
    """Raised when no selected music provider is available."""

    def __init__(
        self,
        message: str = "No music provider is currently available.",
    ) -> None:
        super().__init__(
            code="PROVIDER_UNAVAILABLE",
            message=message,
        )
