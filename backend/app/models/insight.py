"""Insight models for AI-generated intelligence."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin, UUIDMixin
from app.models.feedback import Urgency

if TYPE_CHECKING:
    from app.models.product import Product


class InsightType(str, Enum):
    """Types of AI-generated insights."""

    MARKETING_OPPORTUNITY = "marketing_opportunity"
    CHURN_RISK = "churn_risk"
    FEATURE_DEMAND = "feature_demand"
    COMPETITOR_INSIGHT = "competitor_insight"
    SENTIMENT_SHIFT = "sentiment_shift"
    TRENDING_TOPIC = "trending_topic"
    ACTION_REQUIRED = "action_required"


class DeepAnalysisType(str, Enum):
    """Types of deep analysis available."""

    CHURN_ANALYSIS = "churn_analysis"
    COMPETITOR_INTELLIGENCE = "competitor_intelligence"
    CONTENT_STRATEGY = "content_strategy"


class DeepAnalysisStatus(str, Enum):
    """Status of deep analysis."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FeedbackTheme(Base, UUIDMixin, TimestampMixin):
    """Auto-clustered theme from feedback."""

    __tablename__ = "feedback_themes"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sentiment_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    urgency: Mapped[Urgency] = mapped_column(
        String(50), default=Urgency.MEDIUM, nullable=False
    )
    sample_feedback_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="feedback_themes")

    # Indexes
    __table_args__ = (
        Index("ix_feedback_themes_product_id", "product_id"),
        Index("ix_feedback_themes_product_active", "product_id", "is_active"),
    )


class WeeklyReport(Base, UUIDMixin, TimestampMixin):
    """Automated weekly summary."""

    __tablename__ = "weekly_reports"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    week_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    week_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Marketing metrics
    posts_published: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_conversions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    best_performing_post: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Feedback metrics
    new_mentions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sentiment_change: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    top_complaints: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    top_praise: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)

    # AI-generated content
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    marketing_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sentiment_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommended_actions: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    next_week_focus: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Delivery tracking
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="weekly_reports")

    # Indexes
    __table_args__ = (
        Index("ix_weekly_reports_product_id", "product_id"),
        Index("ix_weekly_reports_product_week", "product_id", "week_start"),
    )


class Insight(Base, UUIDMixin, TimestampMixin):
    """An AI-generated insight or recommendation."""

    __tablename__ = "insights"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[InsightType] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[Urgency] = mapped_column(
        String(50), default=Urgency.MEDIUM, nullable=False
    )
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    suggested_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    source: Mapped[str] = mapped_column(String(100), default="weekly_report", nullable=False)
    is_actioned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    actioned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="insights")

    # Indexes
    __table_args__ = (
        Index("ix_insights_product_id", "product_id"),
        Index("ix_insights_product_type", "product_id", "type"),
        Index("ix_insights_product_actioned", "product_id", "is_actioned"),
    )


class DeepAnalysis(Base, UUIDMixin, TimestampMixin):
    """Deep analysis request and results (Pro+ feature)."""

    __tablename__ = "deep_analyses"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    analysis_type: Mapped[DeepAnalysisType] = mapped_column(String(50), nullable=False)
    status: Mapped[DeepAnalysisStatus] = mapped_column(
        String(50), default=DeepAnalysisStatus.PENDING, nullable=False
    )

    # Results
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    data_points_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="deep_analyses")

    # Indexes
    __table_args__ = (
        Index("ix_deep_analyses_product_id", "product_id"),
        Index("ix_deep_analyses_org_id", "organization_id"),
        Index("ix_deep_analyses_status", "status"),
    )
