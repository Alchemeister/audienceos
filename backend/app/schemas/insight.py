"""Insight schemas for Phase 4: Insights & Intelligence."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import BaseSchema, Urgency


# =========================================================================
# Enums
# =========================================================================


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


# =========================================================================
# Theme Clustering Schemas
# =========================================================================


class ThemeClusterRequest(BaseSchema):
    """Request to trigger theme clustering for a product."""

    force_recluster: bool = Field(
        False, description="Force re-clustering even if recent clusters exist"
    )
    min_feedback_count: int = Field(
        10, ge=5, le=100, description="Minimum feedback items to include in clustering"
    )


class FeedbackThemeResponse(BaseSchema):
    """Response schema for a feedback theme."""

    id: uuid.UUID
    product_id: uuid.UUID
    name: str
    description: str
    feedback_count: int
    sentiment_breakdown: dict[str, int]
    urgency: str
    sample_feedback_ids: list[str]
    keywords: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ThemeListResponse(BaseSchema):
    """List of feedback themes."""

    themes: list[FeedbackThemeResponse]
    total: int
    last_clustered_at: datetime | None = None


class ThemeClusterResponse(BaseSchema):
    """Response after triggering theme clustering."""

    task_id: str
    status: str
    message: str


# =========================================================================
# Weekly Report Schemas
# =========================================================================


class WeeklyReportSummary(BaseSchema):
    """Brief summary of a weekly report."""

    id: uuid.UUID
    product_id: uuid.UUID
    week_start: datetime
    week_end: datetime
    new_mentions: int
    sentiment_score: float
    sentiment_change: float
    email_sent: bool
    created_at: datetime


class MarketingPerformance(BaseSchema):
    """Marketing performance section of weekly report."""

    key_metrics: dict[str, Any]
    best_content: str | None
    worst_content: str | None
    conversion_insights: str | None


class SentimentAnalysis(BaseSchema):
    """Sentiment analysis section of weekly report."""

    trend: str
    top_complaints: list[dict[str, Any]]
    top_praise: list[dict[str, Any]]
    notable_changes: str | None


class RecommendedAction(BaseSchema):
    """A recommended action from the report."""

    priority: str
    action: str
    reason: str


class NextWeekFocus(BaseSchema):
    """Next week focus section of weekly report."""

    topics: list[str]
    subreddits: list[str]
    trending: str | None


class WeeklyReportResponse(BaseSchema):
    """Full weekly report response."""

    id: uuid.UUID
    product_id: uuid.UUID
    week_start: datetime
    week_end: datetime

    # Marketing metrics
    posts_published: int
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    best_performing_post: str | None

    # Feedback metrics
    new_mentions: int
    sentiment_score: float = Field(..., ge=-1, le=1)
    sentiment_change: float
    top_complaints: list[dict[str, Any]]
    top_praise: list[dict[str, Any]]

    # AI-generated content
    executive_summary: str | None
    marketing_analysis: dict[str, Any] | None
    sentiment_analysis: dict[str, Any] | None
    recommended_actions: list[dict[str, Any]]
    next_week_focus: dict[str, Any] | None

    # Delivery
    email_sent: bool
    email_sent_at: datetime | None

    created_at: datetime


class WeeklyReportListResponse(BaseSchema):
    """List of weekly reports."""

    reports: list[WeeklyReportSummary]
    total: int


# =========================================================================
# Insight Schemas
# =========================================================================


class InsightResponse(BaseSchema):
    """Response schema for an insight."""

    id: uuid.UUID
    product_id: uuid.UUID
    type: str
    title: str
    description: str
    priority: str
    evidence: list[str]
    suggested_action: str | None
    confidence: float = Field(..., ge=0, le=1)
    source: str
    is_actioned: bool
    actioned_at: datetime | None
    is_dismissed: bool
    created_at: datetime
    updated_at: datetime


class InsightListResponse(BaseSchema):
    """List of insights."""

    insights: list[InsightResponse]
    total: int


class InsightActionRequest(BaseSchema):
    """Request to mark an insight as actioned or dismissed."""

    is_actioned: bool = False
    is_dismissed: bool = False


# =========================================================================
# Deep Analysis Schemas (Pro+ Feature)
# =========================================================================


class DeepAnalysisRequest(BaseSchema):
    """Request to trigger a deep analysis."""

    analysis_type: DeepAnalysisType
    parameters: dict[str, Any] = Field(default_factory=dict)


class DeepAnalysisResponse(BaseSchema):
    """Response schema for a deep analysis."""

    id: uuid.UUID
    product_id: uuid.UUID
    organization_id: uuid.UUID
    analysis_type: str
    status: str
    results: dict[str, Any] | None
    summary: str | None
    recommendations: list[dict[str, Any]]
    data_points_analyzed: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DeepAnalysisListResponse(BaseSchema):
    """List of deep analyses."""

    analyses: list[DeepAnalysisResponse]
    total: int


class CreditsResponse(BaseSchema):
    """Response showing available deep analysis credits."""

    tier: str
    credits_remaining: int
    credits_total: int
    is_unlimited: bool
    reset_at: datetime | None


# =========================================================================
# Clustering Task Response
# =========================================================================


class ClusteringTaskResponse(BaseSchema):
    """Response from clustering task."""

    product_id: str
    themes_created: int
    feedback_processed: int
    status: str
