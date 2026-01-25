"""Product model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.audience import AudienceResearch, AudienceSource
    from app.models.campaign import Campaign
    from app.models.feedback import FeedbackItem
    from app.models.insight import DeepAnalysis, FeedbackTheme, Insight, WeeklyReport
    from app.models.search_state import KeywordSearchState
    from app.models.user import Organization


class Product(Base, UUIDMixin, TimestampMixin):
    """A product/project being tracked."""

    __tablename__ = "products"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    competitors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Tracking for incremental feedback collection
    feedback_last_collected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # When historical backfill was completed (one-time on signup)
    backfill_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="products"
    )
    audience_sources: Mapped[list["AudienceSource"]] = relationship(
        "AudienceSource", back_populates="product", cascade="all, delete-orphan"
    )
    audience_researches: Mapped[list["AudienceResearch"]] = relationship(
        "AudienceResearch", back_populates="product", cascade="all, delete-orphan"
    )
    feedback_items: Mapped[list["FeedbackItem"]] = relationship(
        "FeedbackItem", back_populates="product", cascade="all, delete-orphan"
    )
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign", back_populates="product", cascade="all, delete-orphan"
    )
    feedback_themes: Mapped[list["FeedbackTheme"]] = relationship(
        "FeedbackTheme", back_populates="product", cascade="all, delete-orphan"
    )
    weekly_reports: Mapped[list["WeeklyReport"]] = relationship(
        "WeeklyReport", back_populates="product", cascade="all, delete-orphan"
    )
    insights: Mapped[list["Insight"]] = relationship(
        "Insight", back_populates="product", cascade="all, delete-orphan"
    )
    deep_analyses: Mapped[list["DeepAnalysis"]] = relationship(
        "DeepAnalysis", back_populates="product", cascade="all, delete-orphan"
    )
    keyword_search_states: Mapped[list["KeywordSearchState"]] = relationship(
        "KeywordSearchState", back_populates="product", cascade="all, delete-orphan"
    )
