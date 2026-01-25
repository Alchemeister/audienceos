"""Billing and subscription schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field

from app.schemas.common import BaseSchema, SubscriptionTier


class SubscriptionStatus(str, Enum):
    """Subscription status."""

    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


# ==================== Subscription Schemas ====================


class SubscriptionBase(BaseSchema):
    """Base subscription fields."""

    tier: SubscriptionTier
    status: SubscriptionStatus


class SubscriptionResponse(SubscriptionBase):
    """Subscription response."""

    id: UUID
    organization_id: UUID
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime


class SubscribeRequest(BaseSchema):
    """Request to subscribe/change subscription."""

    tier: SubscriptionTier = Field(..., description="The tier to subscribe to")


class CancelSubscriptionRequest(BaseSchema):
    """Request to cancel subscription."""

    immediate: bool = Field(
        default=False,
        description="If true, cancel immediately. If false, cancel at period end.",
    )


# ==================== Usage Schemas ====================


class UsageLimitInfo(BaseSchema):
    """Information about a single usage limit."""

    current: int = Field(..., description="Current usage count")
    limit: int = Field(..., description="Maximum allowed (-1 for unlimited)")
    percentage: float = Field(..., description="Percentage used (0-100, null if unlimited)")
    is_unlimited: bool = Field(..., description="Whether this limit is unlimited")


class UsageResponse(BaseSchema):
    """Current usage information."""

    organization_id: UUID
    period_start: datetime
    period_end: datetime
    products: UsageLimitInfo
    keywords: UsageLimitInfo
    feedback: UsageLimitInfo
    deep_analysis: UsageLimitInfo


class UsageRecordResponse(BaseSchema):
    """Full usage record response."""

    id: UUID
    organization_id: UUID
    period_start: datetime
    period_end: datetime
    feedback_count: int
    keywords_count: int
    deep_analysis_used: int
    products_count: int
    created_at: datetime


# ==================== Plan Schemas ====================


class PlanFeatures(BaseSchema):
    """Features included in a plan."""

    products: int = Field(..., description="Number of products allowed (-1 for unlimited)")
    keywords: int = Field(..., description="Number of keywords allowed (-1 for unlimited)")
    feedback_per_month: int = Field(..., description="Monthly feedback limit (-1 for unlimited)")
    backfill_days: int = Field(..., description="Days of historical backfill")
    deep_analysis_credits: int = Field(..., description="Monthly deep analysis credits (-1 for unlimited)")


class PlanResponse(BaseSchema):
    """Plan/tier information."""

    tier: SubscriptionTier
    name: str
    description: str
    price_cents: int
    price_display: str
    features: PlanFeatures
    is_current: bool = False


class PlansListResponse(BaseSchema):
    """List of available plans."""

    plans: list[PlanResponse]
    current_tier: SubscriptionTier


# ==================== Billing Event Schemas ====================


class BillingEventResponse(BaseSchema):
    """Billing event response."""

    id: UUID
    organization_id: UUID
    event_type: str
    metadata: dict | None
    created_at: datetime


class BillingEventsListResponse(BaseSchema):
    """List of billing events."""

    items: list[BillingEventResponse]
    total: int


# ==================== Invoice Schemas (Stubs for Stripe) ====================


class InvoiceResponse(BaseSchema):
    """Invoice response (stub for Stripe integration)."""

    id: str
    amount_due: int
    amount_paid: int
    status: str
    created: datetime
    invoice_pdf: str | None = None
    hosted_invoice_url: str | None = None


class InvoicesListResponse(BaseSchema):
    """List of invoices."""

    items: list[InvoiceResponse]
    has_more: bool = False


# ==================== Portal Schemas ====================


class BillingPortalResponse(BaseSchema):
    """Billing portal session response."""

    url: str | None = Field(
        None,
        description="URL to Stripe billing portal (null if not available)",
    )
