"""Custom exception classes for AudienceOS."""

from typing import Any


class AudienceOSError(Exception):
    """Base exception for all AudienceOS errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AudienceOSError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            details={"resource": resource, "identifier": identifier},
        )


class ValidationError(AudienceOSError):
    """Validation failed."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None):
        super().__init__(
            message=message,
            details={"errors": errors or []},
        )


class AIServiceError(AudienceOSError):
    """AI service (Claude, DeepSeek) error."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: int | None = None,
    ):
        super().__init__(
            message=message,
            details={"provider": provider, "status_code": status_code},
        )


class ExternalAPIError(AudienceOSError):
    """External API (Reddit, Twitter, etc.) error."""

    def __init__(
        self,
        message: str,
        service: str,
        status_code: int | None = None,
    ):
        super().__init__(
            message=message,
            details={"service": service, "status_code": status_code},
        )


class RateLimitError(AudienceOSError):
    """Rate limit exceeded."""

    def __init__(self, service: str, retry_after: int | None = None):
        super().__init__(
            message=f"Rate limit exceeded for {service}",
            details={"service": service, "retry_after": retry_after},
        )


class AuthenticationError(AudienceOSError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message)


class AuthorizationError(AudienceOSError):
    """Authorization failed (insufficient permissions)."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message)


class TierLimitError(AudienceOSError):
    """Subscription tier limit reached."""

    def __init__(self, feature: str, current_tier: str, required_tier: str | None = None):
        message = f"Feature '{feature}' limit reached on {current_tier} tier"
        if required_tier:
            message += f". Upgrade to {required_tier} for more."
        super().__init__(
            message=message,
            details={
                "feature": feature,
                "current_tier": current_tier,
                "required_tier": required_tier,
            },
        )
