"""User and Organization models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin, UUIDMixin


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""

    INDIE = "indie"
    PRO = "pro"
    AGENCY = "agency"


# Deep analysis credits by tier
DEEP_ANALYSIS_CREDITS = {
    SubscriptionTier.INDIE: 0,  # Not available for Indie
    SubscriptionTier.PRO: 4,  # 4 per month
    SubscriptionTier.AGENCY: -1,  # Unlimited (-1 = unlimited)
}


class Organization(Base, UUIDMixin, TimestampMixin):
    """Organization that owns products and users."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        String(50),
        default=SubscriptionTier.INDIE,
        nullable=False,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Deep analysis credits (Pro+)
    deep_analysis_credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credits_reset_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="organization")
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="organization"
    )
    subscription: Mapped["Subscription | None"] = relationship(
        "Subscription", back_populates="organization", uselist=False
    )
    usage_records: Mapped[list["UsageRecord"]] = relationship(
        "UsageRecord", back_populates="organization"
    )
    billing_events: Mapped[list["BillingEvent"]] = relationship(
        "BillingEvent", back_populates="organization"
    )


class User(Base, UUIDMixin, TimestampMixin):
    """User account."""

    __tablename__ = "users"

    clerk_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="users"
    )


# Import models here to avoid circular imports in relationship definitions
from app.models.product import Product  # noqa: E402, F401
from app.models.billing import Subscription, UsageRecord, BillingEvent  # noqa: E402, F401
