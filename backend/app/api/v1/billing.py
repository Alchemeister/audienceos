"""Billing and subscription endpoints."""

import logging
import uuid

from fastapi import APIRouter, status

from app.api.deps import AsyncSessionDep, CurrentUserDep, UsageServiceDep
from app.schemas.billing import (
    BillingEventsListResponse,
    BillingEventResponse,
    BillingPortalResponse,
    CancelSubscriptionRequest,
    InvoicesListResponse,
    PlanResponse,
    PlansListResponse,
    SubscribeRequest,
    SubscriptionResponse,
    SubscriptionStatus,
    UsageLimitInfo,
    UsageResponse,
)
from app.services.billing.subscription import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> SubscriptionResponse:
    """
    Get current subscription details.

    Returns the organization's subscription including tier, status, and billing period.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    service = SubscriptionService(db)

    subscription = await service.get_or_create_subscription(org_id)

    return SubscriptionResponse(
        id=subscription.id,
        organization_id=subscription.organization_id,
        tier=subscription.tier.upper(),
        status=SubscriptionStatus(subscription.status),
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
    )


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: CurrentUserDep,
    usage_service: UsageServiceDep,
) -> UsageResponse:
    """
    Get current period usage vs limits.

    Returns usage statistics for products, keywords, feedback, and deep analysis.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    usage = await usage_service.get_current_usage(org_id)
    percentages = await usage_service.get_usage_percentage(org_id)

    def make_limit_info(key: str) -> UsageLimitInfo:
        info = usage[key]
        return UsageLimitInfo(
            current=info["current"],
            limit=info["limit"],
            percentage=percentages[key] or 0.0,
            is_unlimited=info["is_unlimited"],
        )

    return UsageResponse(
        organization_id=org_id,
        period_start=usage["period_start"],
        period_end=usage["period_end"],
        products=make_limit_info("products"),
        keywords=make_limit_info("keywords"),
        feedback=make_limit_info("feedback"),
        deep_analysis=make_limit_info("deep_analysis"),
    )


@router.get("/plans", response_model=PlansListResponse)
async def get_plans(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> PlansListResponse:
    """
    Get available subscription plans with features and prices.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    service = SubscriptionService(db)

    plans = await service.get_plans(org_id)
    subscription = await service.get_subscription(org_id)

    current_tier = subscription.tier.upper() if subscription else "INDIE"

    return PlansListResponse(
        plans=plans,
        current_tier=current_tier,
    )


@router.post("/subscribe", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
async def subscribe(
    data: SubscribeRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> SubscriptionResponse:
    """
    Subscribe to a plan or change subscription tier.

    For now, this directly updates the subscription tier.
    Later, this will create a Stripe checkout session for payment.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    service = SubscriptionService(db)

    subscription = await service.subscribe(org_id, data.tier.value.lower())

    logger.info(f"Subscription updated: org={org_id} tier={data.tier.value}")

    return SubscriptionResponse(
        id=subscription.id,
        organization_id=subscription.organization_id,
        tier=subscription.tier.upper(),
        status=SubscriptionStatus(subscription.status),
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
    )


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    data: CancelSubscriptionRequest | None = None,
) -> SubscriptionResponse:
    """
    Cancel the current subscription.

    By default, cancellation takes effect at the end of the current billing period.
    Set immediate=true to cancel immediately (downgrade to indie tier).
    """
    org_id = uuid.UUID(current_user["organization_id"])
    service = SubscriptionService(db)

    immediate = data.immediate if data else False
    subscription = await service.cancel(org_id, immediate=immediate)

    logger.info(f"Subscription canceled: org={org_id} immediate={immediate}")

    return SubscriptionResponse(
        id=subscription.id,
        organization_id=subscription.organization_id,
        tier=subscription.tier.upper(),
        status=SubscriptionStatus(subscription.status),
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
    )


@router.post("/reactivate", response_model=SubscriptionResponse)
async def reactivate_subscription(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> SubscriptionResponse:
    """
    Reactivate a subscription that was scheduled to cancel.

    Only works if the subscription was set to cancel at period end
    and the period hasn't ended yet.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    service = SubscriptionService(db)

    subscription = await service.reactivate(org_id)

    return SubscriptionResponse(
        id=subscription.id,
        organization_id=subscription.organization_id,
        tier=subscription.tier.upper(),
        status=SubscriptionStatus(subscription.status),
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
    )


@router.get("/invoices", response_model=InvoicesListResponse)
async def get_invoices(
    current_user: CurrentUserDep,
) -> InvoicesListResponse:
    """
    Get list of invoices.

    Returns empty list for now - will be populated from Stripe later.
    """
    # Stub for Stripe integration
    return InvoicesListResponse(
        items=[],
        has_more=False,
    )


@router.post("/portal", response_model=BillingPortalResponse)
async def create_billing_portal_session(
    current_user: CurrentUserDep,
) -> BillingPortalResponse:
    """
    Create a Stripe billing portal session.

    Returns null URL for now - will return Stripe portal URL later.
    """
    # Stub for Stripe integration
    return BillingPortalResponse(url=None)


@router.get("/events", response_model=BillingEventsListResponse)
async def get_billing_events(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    limit: int = 50,
    offset: int = 0,
) -> BillingEventsListResponse:
    """
    Get billing event history.

    Returns a log of subscription changes, payments, etc.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    service = SubscriptionService(db)

    events, total = await service.get_billing_events(org_id, limit, offset)

    return BillingEventsListResponse(
        items=[
            BillingEventResponse(
                id=e.id,
                organization_id=e.organization_id,
                event_type=e.event_type,
                metadata=e.metadata,
                created_at=e.created_at,
            )
            for e in events
        ],
        total=total,
    )
