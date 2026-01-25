"""Billing and subscription models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, PortableJSON, TimestampMixin, UUIDMixin


class SubscriptionStatus(str, Enum):
    """Subscription status."""

    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


class BillingEventType(str, Enum):
    """Types of billing events."""

    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPGRADED = "subscription_upgraded"
    SUBSCRIPTION_DOWNGRADED = "subscription_downgraded"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    SUBSCRIPTION_REACTIVATED = "subscription_reactivated"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDED = "trial_ended"


class Subscription(Base, UUIDMixin, TimestampMixin):
    """Subscription record for an organization."""

    __tablename__ = "subscriptions"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    tier: Mapped[str] = mapped_column(
        String(50),
        default="indie",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=SubscriptionStatus.ACTIVE.value,
        nullable=False,
    )
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Stripe fields (for later integration)
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="subscription",
    )

    __table_args__ = (
        Index("ix_subscriptions_stripe_subscription_id", "stripe_subscription_id"),
        Index("ix_subscriptions_status", "status"),
    )


class UsageRecord(Base, UUIDMixin):
    """Monthly usage tracking for an organization."""

    __tablename__ = "usage_records"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    feedback_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    keywords_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    deep_analysis_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    products_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="usage_records",
    )

    __table_args__ = (
        Index("ix_usage_records_org_period", "organization_id", "period_start"),
    )


class BillingEvent(Base, UUIDMixin):
    """Audit log for billing events."""

    __tablename__ = "billing_events"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_metadata: Mapped[dict | None] = mapped_column(
        PortableJSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="billing_events",
    )

    __table_args__ = (
        Index("ix_billing_events_org_type", "organization_id", "event_type"),
        Index("ix_billing_events_created", "created_at"),
    )


# Import Organization to avoid circular imports
from app.models.user import Organization  # noqa: E402, F401
