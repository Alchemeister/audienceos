"""Security and authentication utilities."""

from typing import Any

from app.core.exceptions import AuthenticationError


async def verify_clerk_token(token: str) -> dict[str, Any]:
    """
    Verify a Clerk JWT token and return user claims.

    TODO: Implement actual Clerk verification.
    For now, returns a mock user for development.
    """
    if not token:
        raise AuthenticationError("No token provided")

    # TODO: Implement actual Clerk JWT verification
    # This is a stub for development - use the same org_id as the dev seed data
    return {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "email": "dev@example.com",
        "organization_id": "00000000-0000-0000-0000-000000000001",
    }


def generate_api_key() -> str:
    """Generate a new API key for an organization."""
    import secrets

    return f"aos_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    import hashlib

    return hashlib.sha256(api_key.encode()).hexdigest()

