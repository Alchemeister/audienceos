"""Background tasks for billing and usage management."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from celery import shared_task
from sqlalchemy import select

from app.core.config import get_settings
from app.core.tiers import get_tier_limits
from app.db.session import async_session_factory
from app.models.billing import Subscription, UsageRecord
from app.models.user import Organization, SubscriptionTier
from app.services.billing.subscription import SubscriptionService
from app.services.billing.usage import UsageService

logger = logging.getLogger(__name__)
settings = get_settings()


def run_async(coro):
    """Run async function in sync context for Celery."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task
def reset_all_monthly_usage() -> dict[str, Any]:
    """
    Reset monthly usage counters for all organizations.

    Should be scheduled to run on the 1st of each month.
    """
    return run_async(_reset_all_monthly_usage())


async def _reset_all_monthly_usage() -> dict[str, Any]:
    """Async implementation of monthly usage reset."""
    async with async_session_factory() as db:
        # Get all organizations
        result = await db.execute(select(Organization.id))
        org_ids = [row[0] for row in result.all()]

        usage_service = UsageService(db)
        reset_count = 0
        errors = []

        for org_id in org_ids:
            try:
                await usage_service.reset_monthly_usage(org_id)
                reset_count += 1
            except Exception as e:
                logger.error(f"Error resetting usage for org {org_id}: {e}")
                errors.append({"org_id": str(org_id), "error": str(e)})

        await db.commit()

        logger.info(f"Monthly usage reset: {reset_count} organizations, {len(errors)} errors")

        return {
            "reset_count": reset_count,
            "total_organizations": len(org_ids),
            "errors": errors,
        }


@shared_task
def reset_deep_analysis_credits() -> dict[str, Any]:
    """
    Reset deep analysis credits for Pro tier users.

    Should be scheduled to run on the 1st of each month.
    Agency users have unlimited credits (-1), Indie users have 0 credits.
    """
    return run_async(_reset_deep_analysis_credits())


async def _reset_deep_analysis_credits() -> dict[str, Any]:
    """Async implementation of deep analysis credit reset."""
    async with async_session_factory() as db:
        now = datetime.now(timezone.utc)

        # Get all organizations
        result = await db.execute(select(Organization))
        organizations = result.scalars().all()

        reset_count = 0
        skipped_count = 0

        for org in organizations:
            tier = org.subscription_tier.value.lower() if org.subscription_tier else "indie"
            limits = get_tier_limits(tier)
            credits = limits["deep_analysis_credits"]

            if credits == -1:
                # Unlimited tier (agency) - no reset needed
                skipped_count += 1
                continue

            # Reset credits to tier limit
            org.deep_analysis_credits = credits
            org.credits_reset_at = now
            reset_count += 1

        await db.commit()

        logger.info(
            f"Deep analysis credits reset: {reset_count} organizations reset, "
            f"{skipped_count} skipped (unlimited)"
        )

        return {
            "reset_count": reset_count,
            "skipped_count": skipped_count,
            "total_organizations": len(organizations),
        }


@shared_task
def process_subscription_period_ends() -> dict[str, Any]:
    """
    Process subscriptions that have reached their period end.

    Handles:
    - Subscriptions set to cancel at period end
    - Subscription renewals

    Should be scheduled to run daily.
    """
    return run_async(_process_subscription_period_ends())


async def _process_subscription_period_ends() -> dict[str, Any]:
    """Async implementation of subscription period end processing."""
    async with async_session_factory() as db:
        now = datetime.now(timezone.utc)

        # Find subscriptions that need processing
        result = await db.execute(
            select(Subscription).where(
                Subscription.current_period_end <= now,
                Subscription.cancel_at_period_end == True,
            )
        )
        subscriptions = result.scalars().all()

        service = SubscriptionService(db)
        processed_count = 0
        errors = []

        for subscription in subscriptions:
            try:
                await service.process_period_end(subscription.organization_id)
                processed_count += 1
            except Exception as e:
                logger.error(
                    f"Error processing period end for org {subscription.organization_id}: {e}"
                )
                errors.append({
                    "org_id": str(subscription.organization_id),
                    "error": str(e),
                })

        await db.commit()

        logger.info(
            f"Subscription period ends processed: {processed_count} subscriptions, "
            f"{len(errors)} errors"
        )

        return {
            "processed_count": processed_count,
            "total_subscriptions": len(subscriptions),
            "errors": errors,
        }


@shared_task
def check_usage_limits() -> dict[str, Any]:
    """
    Check usage limits and send warnings if approaching limits.

    Should be scheduled to run daily.
    """
    return run_async(_check_usage_limits())


async def _check_usage_limits() -> dict[str, Any]:
    """Async implementation of usage limit checking."""
    async with async_session_factory() as db:
        # Get all organizations
        result = await db.execute(select(Organization.id))
        org_ids = [row[0] for row in result.all()]

        usage_service = UsageService(db)
        warnings = []

        for org_id in org_ids:
            try:
                percentages = await usage_service.get_usage_percentage(org_id)

                # Check if any limit is above 80%
                for limit_type, percentage in percentages.items():
                    if percentage is not None and percentage >= 80:
                        warnings.append({
                            "org_id": str(org_id),
                            "limit_type": limit_type,
                            "percentage": percentage,
                        })
                        logger.warning(
                            f"Usage warning: org={org_id} {limit_type}={percentage:.1f}%"
                        )

            except Exception as e:
                logger.error(f"Error checking usage for org {org_id}: {e}")

        logger.info(f"Usage limit check complete: {len(warnings)} warnings")

        return {
            "total_organizations": len(org_ids),
            "warnings": warnings,
        }
