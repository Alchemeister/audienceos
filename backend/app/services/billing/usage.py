"""Usage tracking service for billing limits."""

import uuid
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TierLimitError
from app.core.tiers import TIER_LIMITS, check_within_limit, get_tier_limits, is_unlimited
from app.models.billing import UsageRecord
from app.models.product import Product
from app.models.user import Organization


LimitType = Literal["products", "keywords", "feedback", "deep_analysis"]


class UsageService:
    """Service for tracking and enforcing usage limits."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_organization_tier(self, org_id: uuid.UUID) -> str:
        """Get the subscription tier for an organization."""
        result = await self.db.execute(
            select(Organization.subscription_tier).where(Organization.id == org_id)
        )
        tier = result.scalar_one_or_none()
        return tier.value if tier else "indie"

    async def get_current_period(self) -> tuple[datetime, datetime]:
        """Get the current billing period (month boundaries)."""
        now = datetime.now(timezone.utc)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate period end (first of next month)
        if now.month == 12:
            period_end = period_start.replace(year=now.year + 1, month=1)
        else:
            period_end = period_start.replace(month=now.month + 1)

        return period_start, period_end

    async def get_or_create_usage_record(self, org_id: uuid.UUID) -> UsageRecord:
        """Get or create usage record for current period."""
        period_start, period_end = await self.get_current_period()

        # Try to find existing record
        result = await self.db.execute(
            select(UsageRecord).where(
                UsageRecord.organization_id == org_id,
                UsageRecord.period_start == period_start,
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            # Create new record for this period
            record = UsageRecord(
                organization_id=org_id,
                period_start=period_start,
                period_end=period_end,
                feedback_count=0,
                keywords_count=0,
                deep_analysis_used=0,
                products_count=await self._count_products(org_id),
            )
            self.db.add(record)
            await self.db.flush()

        return record

    async def _count_products(self, org_id: uuid.UUID) -> int:
        """Count current products for an organization."""
        result = await self.db.execute(
            select(func.count(Product.id)).where(Product.organization_id == org_id)
        )
        return result.scalar() or 0

    async def _count_keywords(self, org_id: uuid.UUID) -> int:
        """Count total keywords across all products for an organization."""
        result = await self.db.execute(
            select(Product.keywords).where(Product.organization_id == org_id)
        )
        products = result.scalars().all()

        total_keywords = 0
        for keywords in products:
            if keywords:
                total_keywords += len(keywords)

        return total_keywords

    async def get_current_usage(self, org_id: uuid.UUID) -> dict:
        """
        Get current usage statistics for an organization.

        Returns dict with current usage counts and limits.
        """
        tier = await self.get_organization_tier(org_id)
        limits = get_tier_limits(tier)
        record = await self.get_or_create_usage_record(org_id)

        # Get actual product and keyword counts
        products_count = await self._count_products(org_id)
        keywords_count = await self._count_keywords(org_id)

        # Update record with current counts
        record.products_count = products_count
        record.keywords_count = keywords_count

        period_start, period_end = await self.get_current_period()

        return {
            "organization_id": org_id,
            "tier": tier,
            "period_start": period_start,
            "period_end": period_end,
            "products": {
                "current": products_count,
                "limit": limits["products"],
                "is_unlimited": is_unlimited(limits["products"]),
            },
            "keywords": {
                "current": keywords_count,
                "limit": limits["keywords"],
                "is_unlimited": is_unlimited(limits["keywords"]),
            },
            "feedback": {
                "current": record.feedback_count,
                "limit": limits["feedback_per_month"],
                "is_unlimited": is_unlimited(limits["feedback_per_month"]),
            },
            "deep_analysis": {
                "current": record.deep_analysis_used,
                "limit": limits["deep_analysis_credits"],
                "is_unlimited": is_unlimited(limits["deep_analysis_credits"]),
            },
        }

    async def check_limit(self, org_id: uuid.UUID, limit_type: LimitType) -> bool:
        """
        Check if an organization can perform an action based on limits.

        Returns True if within limits, False if limit reached.
        """
        usage = await self.get_current_usage(org_id)
        limit_info = usage.get(limit_type, {})

        if limit_info.get("is_unlimited"):
            return True

        return check_within_limit(limit_info["current"], limit_info["limit"])

    async def enforce_limit(
        self,
        org_id: uuid.UUID,
        limit_type: LimitType,
        required_tier: str | None = None,
    ) -> None:
        """
        Enforce a limit, raising TierLimitError if exceeded.

        Args:
            org_id: Organization UUID
            limit_type: Type of limit to check
            required_tier: Optional tier to suggest for upgrade
        """
        if not await self.check_limit(org_id, limit_type):
            tier = await self.get_organization_tier(org_id)
            raise TierLimitError(
                feature=limit_type,
                current_tier=tier,
                required_tier=required_tier,
            )

    async def increment_usage(
        self,
        org_id: uuid.UUID,
        limit_type: LimitType,
        amount: int = 1,
    ) -> None:
        """
        Increment usage for a specific limit type.

        Args:
            org_id: Organization UUID
            limit_type: Type of usage to increment
            amount: Amount to increment by
        """
        record = await self.get_or_create_usage_record(org_id)

        if limit_type == "feedback":
            record.feedback_count += amount
        elif limit_type == "deep_analysis":
            record.deep_analysis_used += amount
        elif limit_type == "products":
            record.products_count = await self._count_products(org_id)
        elif limit_type == "keywords":
            record.keywords_count = await self._count_keywords(org_id)

        await self.db.flush()

    async def reset_monthly_usage(self, org_id: uuid.UUID) -> UsageRecord:
        """
        Reset monthly usage counters for a new period.

        Called by cron job on the 1st of each month.
        """
        period_start, period_end = await self.get_current_period()

        # Create fresh record for new period
        record = UsageRecord(
            organization_id=org_id,
            period_start=period_start,
            period_end=period_end,
            feedback_count=0,
            keywords_count=await self._count_keywords(org_id),
            deep_analysis_used=0,
            products_count=await self._count_products(org_id),
        )
        self.db.add(record)
        await self.db.flush()

        return record

    async def get_usage_percentage(self, org_id: uuid.UUID) -> dict:
        """
        Get usage as percentages of limits.

        Returns dict with percentage for each limit (null if unlimited).
        """
        usage = await self.get_current_usage(org_id)

        def calc_percentage(info: dict) -> float | None:
            if info.get("is_unlimited"):
                return None
            if info["limit"] <= 0:
                return 100.0 if info["current"] > 0 else 0.0
            return min(100.0, (info["current"] / info["limit"]) * 100)

        return {
            "products": calc_percentage(usage["products"]),
            "keywords": calc_percentage(usage["keywords"]),
            "feedback": calc_percentage(usage["feedback"]),
            "deep_analysis": calc_percentage(usage["deep_analysis"]),
        }
