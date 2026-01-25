"""Subscription tier limits and configuration."""

from enum import Enum
from typing import TypedDict


class TierLimits(TypedDict):
    """Type definition for tier limits."""

    products: int  # -1 = unlimited
    keywords: int  # -1 = unlimited
    feedback_per_month: int  # -1 = unlimited
    backfill_days: int
    deep_analysis_credits: int  # -1 = unlimited
    price_cents: int


TIER_LIMITS: dict[str, TierLimits] = {
    "indie": {
        "products": 1,
        "keywords": 10,
        "feedback_per_month": 500,
        "backfill_days": 14,
        "deep_analysis_credits": 0,
        "price_cents": 3900,
    },
    "pro": {
        "products": 3,
        "keywords": 50,
        "feedback_per_month": 5000,
        "backfill_days": 90,
        "deep_analysis_credits": 4,
        "price_cents": 9900,
    },
    "agency": {
        "products": -1,  # unlimited
        "keywords": -1,  # unlimited
        "feedback_per_month": -1,  # unlimited
        "backfill_days": 180,
        "deep_analysis_credits": -1,  # unlimited
        "price_cents": 29900,
    },
}


def get_tier_limits(tier: str) -> TierLimits:
    """Get limits for a subscription tier."""
    return TIER_LIMITS.get(tier.lower(), TIER_LIMITS["indie"])


def is_unlimited(limit: int) -> bool:
    """Check if a limit value represents unlimited (-1)."""
    return limit == -1


def check_within_limit(current: int, limit: int) -> bool:
    """Check if current usage is within the limit."""
    if is_unlimited(limit):
        return True
    return current < limit
