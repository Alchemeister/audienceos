"""Feedback models."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audience import Platform
from app.models.base import Base, GUID, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Product


class Sentiment(str, Enum):
    """Sentiment classification."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class FeedbackCategory(str, Enum):
    """Feedback category classification."""

    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    PRAISE = "praise"
    COMPLAINT = "complaint"
    QUESTION = "question"
    CHURN_RISK = "churn_risk"
    COMPETITOR_MENTION = "competitor_mention"


class Urgency(str, Enum):
    """Urgency level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackItem(Base, UUIDMixin, TimestampMixin):
    """A single piece of feedback from any source."""

    __tablename__ = "feedback_items"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[Platform] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[Sentiment] = mapped_column(String(50), nullable=False)
    emotion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[FeedbackCategory] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    urgency: Mapped[Urgency] = mapped_column(
        String(50), default=Urgency.MEDIUM, nullable=False
    )
    product_area: Mapped[str | None] = mapped_column(String(255), nullable=True)
    key_phrases: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    churn_risk: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    suggested_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_actioned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    actioned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="feedback_items")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_feedback_items_product_source", "product_id", "source"),
        Index("ix_feedback_items_product_sentiment", "product_id", "sentiment"),
        Index("ix_feedback_items_product_category", "product_id", "category"),
        Index("ix_feedback_items_product_created", "product_id", "created_at"),
    )
