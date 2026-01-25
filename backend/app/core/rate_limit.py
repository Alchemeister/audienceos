"""Rate limiting middleware for API protection.

Security measure #7 from SECURITY.md: Put a speed limit on buttons.
Prevents bots from spamming expensive operations.
"""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse


def get_key_func(request: Request) -> str:
    """
    Get rate limit key from request.

    Uses IP address for public endpoints.
    For authenticated endpoints, could use user ID for per-user limits.
    """
    # Get forwarded IP if behind proxy, otherwise use direct IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(key_func=get_key_func)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.

    Returns a 429 response with Retry-After header as per SECURITY.md.
    """
    # Parse retry_after from the exception message if available
    retry_after = 60  # Default to 60 seconds

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit",
            "message": "Too many requests. Please slow down.",
            "details": {
                "retry_after": retry_after,
            },
        },
        headers={"Retry-After": str(retry_after)},
    )


# Rate limit constants per SECURITY.md
# Auth endpoints (login/register): 5/minute
AUTH_RATE_LIMIT = "5/minute"

# AI generation (expensive operations): 10-30/minute depending on tier
AI_RATE_LIMIT_INDIE = "10/minute"
AI_RATE_LIMIT_PRO = "20/minute"
AI_RATE_LIMIT_AGENCY = "30/minute"

# Standard read endpoints: 100-500/minute
READ_RATE_LIMIT = "100/minute"
READ_RATE_LIMIT_PRO = "300/minute"
READ_RATE_LIMIT_AGENCY = "500/minute"

# Write/mutation endpoints: 30/minute
WRITE_RATE_LIMIT = "30/minute"

# Public tracking endpoints (click tracking): higher limit
TRACKING_RATE_LIMIT = "200/minute"
