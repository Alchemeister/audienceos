"""Shared API dependencies."""

import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, TierLimitError
from app.core.security import verify_clerk_token
from app.core.tiers import TIER_LIMITS
from app.db.session import get_async_session
from app.services.ai.router import AIRouter
from app.services.billing.usage import UsageService

# Type aliases for cleaner dependency injection
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """
    Dependency to get the current authenticated user.

    For development, returns a mock user if no token provided.
    In production, validates the Clerk JWT token.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        User claims dictionary

    Raises:
        HTTPException: If authentication fails
    """
    settings = get_settings()

    # Development mode: always return mock user (skip token verification)
    if settings.APP_ENV == "development":
        return {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "email": "dev@example.com",
            "organization_id": "00000000-0000-0000-0000-000000000001",
            "name": "Dev User",
        }

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return await verify_clerk_token(token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUserDep = Annotated[dict, Depends(get_current_user)]


def get_ai_router(settings: SettingsDep) -> AIRouter:
    """
    Dependency to get the AI router.

    Args:
        settings: Application settings

    Returns:
        Configured AI router instance
    """
    return AIRouter(settings)


AIRouterDep = Annotated[AIRouter, Depends(get_ai_router)]


# ==================== Usage Service Dependency ====================


def get_usage_service(db: AsyncSessionDep) -> UsageService:
    """Get usage service instance."""
    return UsageService(db)


UsageServiceDep = Annotated[UsageService, Depends(get_usage_service)]


# ==================== Tier Enforcement Dependencies ====================


def require_tier(min_tier: str):
    """
    Dependency factory to require a minimum subscription tier.

    Usage:
        @router.post("/premium-feature", dependencies=[Depends(require_tier("pro"))])
    """
    tier_order = {"indie": 0, "pro": 1, "agency": 2}
    min_level = tier_order.get(min_tier.lower(), 0)

    async def check_tier(
        db: AsyncSessionDep,
        current_user: CurrentUserDep,
    ) -> None:
        org_id = uuid.UUID(current_user["organization_id"])
        usage_service = UsageService(db)
        tier = await usage_service.get_organization_tier(org_id)

        current_level = tier_order.get(tier.lower(), 0)
        if current_level < min_level:
            raise TierLimitError(
                feature="this feature",
                current_tier=tier,
                required_tier=min_tier,
            )

    return check_tier


async def check_product_limit(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Dependency to check if organization can create more products.

    Raises TierLimitError if at product limit.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    usage_service = UsageService(db)

    await usage_service.enforce_limit(org_id, "products", required_tier="pro")


async def check_feedback_limit(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Dependency to check if organization can collect more feedback.

    Raises TierLimitError if at feedback limit.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    usage_service = UsageService(db)

    await usage_service.enforce_limit(org_id, "feedback", required_tier="pro")


async def check_deep_analysis_credits(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Dependency to check if organization has deep analysis credits.

    Raises TierLimitError if no credits remaining.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    usage_service = UsageService(db)

    await usage_service.enforce_limit(org_id, "deep_analysis", required_tier="pro")


async def check_keywords_limit(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Dependency to check if organization can add more keywords.

    Raises TierLimitError if at keywords limit.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    usage_service = UsageService(db)

    await usage_service.enforce_limit(org_id, "keywords", required_tier="pro")

