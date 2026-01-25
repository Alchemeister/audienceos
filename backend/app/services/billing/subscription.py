"""Subscription management service."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.tiers import TIER_LIMITS, get_tier_limits
from app.models.billing import BillingEvent, BillingEventType, Subscription, SubscriptionStatus
from app.models.user import Organization, SubscriptionTier
from app.schemas.billing import PlanFeatures, PlanResponse, SubscriptionResponse
from app.schemas.common import SubscriptionTier as SchemaTier

logger = logging.getLogger(__name__)


PLAN_DESCRIPTIONS = {
    "indie": "Perfect for indie hackers and solo founders. Track one product and get started with audience research.",
    "pro": "For growing startups. Track multiple products with advanced analytics and deep analysis.",
    "agency": "Unlimited everything. Perfect for agencies managing multiple clients.",
}


class SubscriptionService:
    """Service for managing subscriptions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_subscription(self, org_id: uuid.UUID) -> Subscription | None:
        """Get subscription for an organization."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.organization_id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_subscription(self, org_id: uuid.UUID) -> Subscription:
        """Get or create subscription for an organization."""
        subscription = await self.get_subscription(org_id)

        if not subscription:
            # Create default subscription
            now = datetime.now(timezone.utc)
            period_end = now + timedelta(days=30)

            subscription = Subscription(
                organization_id=org_id,
                tier="indie",
                status=SubscriptionStatus.ACTIVE.value,
                current_period_start=now,
                current_period_end=period_end,
                cancel_at_period_end=False,
            )
            self.db.add(subscription)

            # Log event
            await self._log_event(
                org_id,
                BillingEventType.SUBSCRIPTION_CREATED,
                {"tier": "indie", "status": "active"},
            )

            await self.db.flush()

        return subscription

    async def subscribe(self, org_id: uuid.UUID, tier: str) -> Subscription:
        """
        Subscribe or change subscription tier.

        For now, this directly updates the tier without Stripe.
        Later, this will create a Stripe checkout session.
        """
        tier = tier.lower()
        if tier not in TIER_LIMITS:
            raise ValidationError(f"Invalid tier: {tier}")

        subscription = await self.get_or_create_subscription(org_id)
        old_tier = subscription.tier

        if old_tier == tier:
            # No change needed
            return subscription

        # Determine event type
        tier_order = {"indie": 0, "pro": 1, "agency": 2}
        if tier_order.get(tier, 0) > tier_order.get(old_tier, 0):
            event_type = BillingEventType.SUBSCRIPTION_UPGRADED
        else:
            event_type = BillingEventType.SUBSCRIPTION_DOWNGRADED

        # Update subscription
        now = datetime.now(timezone.utc)
        subscription.tier = tier
        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=30)
        subscription.cancel_at_period_end = False

        # Update organization tier
        await self._update_org_tier(org_id, tier)

        # Log event
        await self._log_event(
            org_id,
            event_type,
            {"old_tier": old_tier, "new_tier": tier},
        )

        await self.db.flush()

        logger.info(f"Subscription changed: org={org_id} from={old_tier} to={tier}")

        return subscription

    async def cancel(self, org_id: uuid.UUID, immediate: bool = False) -> Subscription:
        """
        Cancel a subscription.

        Args:
            org_id: Organization UUID
            immediate: If True, cancel immediately. If False, cancel at period end.
        """
        subscription = await self.get_subscription(org_id)

        if not subscription:
            raise NotFoundError("Subscription", str(org_id))

        if immediate:
            # Immediate cancellation - downgrade to indie
            subscription.status = SubscriptionStatus.CANCELED.value
            subscription.cancel_at_period_end = False

            # Downgrade to indie tier
            await self._update_org_tier(org_id, "indie")
            subscription.tier = "indie"

            await self._log_event(
                org_id,
                BillingEventType.SUBSCRIPTION_CANCELED,
                {"immediate": True, "previous_tier": subscription.tier},
            )
        else:
            # Cancel at period end
            subscription.cancel_at_period_end = True

            await self._log_event(
                org_id,
                BillingEventType.SUBSCRIPTION_CANCELED,
                {"immediate": False, "cancel_at": subscription.current_period_end.isoformat()},
            )

        await self.db.flush()

        logger.info(f"Subscription canceled: org={org_id} immediate={immediate}")

        return subscription

    async def reactivate(self, org_id: uuid.UUID) -> Subscription:
        """Reactivate a subscription that was set to cancel at period end."""
        subscription = await self.get_subscription(org_id)

        if not subscription:
            raise NotFoundError("Subscription", str(org_id))

        if not subscription.cancel_at_period_end:
            return subscription

        subscription.cancel_at_period_end = False

        await self._log_event(
            org_id,
            BillingEventType.SUBSCRIPTION_REACTIVATED,
            {"tier": subscription.tier},
        )

        await self.db.flush()

        return subscription

    async def get_plans(self, org_id: uuid.UUID | None = None) -> list[PlanResponse]:
        """Get list of available plans."""
        current_tier = None
        if org_id:
            subscription = await self.get_subscription(org_id)
            if subscription:
                current_tier = subscription.tier

        plans = []
        for tier, limits in TIER_LIMITS.items():
            plan = PlanResponse(
                tier=SchemaTier(tier.upper()),
                name=tier.capitalize(),
                description=PLAN_DESCRIPTIONS.get(tier, ""),
                price_cents=limits["price_cents"],
                price_display=f"${limits['price_cents'] / 100:.0f}/mo",
                features=PlanFeatures(
                    products=limits["products"],
                    keywords=limits["keywords"],
                    feedback_per_month=limits["feedback_per_month"],
                    backfill_days=limits["backfill_days"],
                    deep_analysis_credits=limits["deep_analysis_credits"],
                ),
                is_current=(tier == current_tier),
            )
            plans.append(plan)

        return plans

    async def get_billing_events(
        self,
        org_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[BillingEvent], int]:
        """Get billing events for an organization."""
        # Get events
        result = await self.db.execute(
            select(BillingEvent)
            .where(BillingEvent.organization_id == org_id)
            .order_by(BillingEvent.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        events = result.scalars().all()

        # Get total count
        count_result = await self.db.execute(
            select(BillingEvent).where(BillingEvent.organization_id == org_id)
        )
        total = len(count_result.scalars().all())

        return events, total

    async def _update_org_tier(self, org_id: uuid.UUID, tier: str) -> None:
        """Update organization's subscription tier."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = result.scalar_one_or_none()

        if org:
            org.subscription_tier = SubscriptionTier(tier.upper())

            # Reset deep analysis credits based on new tier
            limits = get_tier_limits(tier)
            if limits["deep_analysis_credits"] >= 0:
                org.deep_analysis_credits = limits["deep_analysis_credits"]
            # For unlimited (-1), we don't set a specific value

            org.credits_reset_at = datetime.now(timezone.utc)

    async def _log_event(
        self,
        org_id: uuid.UUID,
        event_type: BillingEventType,
        metadata: dict | None = None,
    ) -> BillingEvent:
        """Log a billing event."""
        event = BillingEvent(
            organization_id=org_id,
            event_type=event_type.value,
            metadata=metadata or {},
        )
        self.db.add(event)
        return event

    async def process_period_end(self, org_id: uuid.UUID) -> None:
        """
        Process subscription at period end.

        Called by cron job to handle subscriptions scheduled to cancel.
        """
        subscription = await self.get_subscription(org_id)

        if not subscription:
            return

        now = datetime.now(timezone.utc)

        if subscription.cancel_at_period_end and now >= subscription.current_period_end:
            # Cancel the subscription
            subscription.status = SubscriptionStatus.CANCELED.value
            subscription.cancel_at_period_end = False

            # Downgrade to indie
            await self._update_org_tier(org_id, "indie")
            subscription.tier = "indie"

            await self._log_event(
                org_id,
                BillingEventType.SUBSCRIPTION_CANCELED,
                {"reason": "period_end"},
            )

            await self.db.flush()

            logger.info(f"Subscription canceled at period end: org={org_id}")
