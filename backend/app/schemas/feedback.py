"""Feedback schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import (
    BaseSchema,
    FeedbackCategory,
    Platform,
    Sentiment,
    Urgency,
)


class FeedbackItemBase(BaseSchema):
    """Base feedback item schema."""

    text: str = Field(..., min_length=1)
    source: Platform
    source_url: str | None = None
    author: str | None = None


class FeedbackItemResponse(BaseSchema):
    """Schema for feedback item response."""

    id: uuid.UUID
    product_id: uuid.UUID
    text: str
    source: str  # Changed to str for flexibility (webhooks can use any source)
    source_url: str | None
    author: str | None
    author_id: str | None
    sentiment: str  # Changed to str for flexibility
    emotion: str | None
    category: str  # Changed to str for flexibility
    subcategory: str | None
    urgency: str  # Changed to str for flexibility
    product_area: str | None
    key_phrases: list[str]
    churn_risk: float = Field(..., ge=0, le=1)
    suggested_action: str | None
    is_actioned: bool
    actioned_at: datetime | None
    collected_at: datetime
    created_at: datetime
    updated_at: datetime


class FeedbackListResponse(BaseSchema):
    """Schema for listing feedback items."""

    items: list[FeedbackItemResponse]
    total: int


class FeedbackAnalyzeRequest(BaseSchema):
    """Schema for analyzing feedback text."""

    text: str = Field(..., min_length=1)
    source: Platform = Platform.MANUAL
    author: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class FeedbackAnalyzeResponse(BaseSchema):
    """Schema for feedback analysis result."""

    sentiment: str
    emotion: str | None
    category: str
    subcategory: str | None
    urgency: str
    product_area: str | None
    key_phrases: list[str]
    churn_risk: float = Field(..., ge=0, le=1)
    suggested_action: str | None


class FeedbackFilterParams(BaseSchema):
    """Schema for filtering feedback."""

    source: Platform | None = None
    sentiment: Sentiment | None = None
    category: FeedbackCategory | None = None
    urgency: Urgency | None = None
    is_actioned: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    search: str | None = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SentimentTrend(BaseSchema):
    """Sentiment trend data point."""

    date: str
    score: float  # -1 to 1
    count: int


class FeedbackStatsResponse(BaseSchema):
    """Schema for feedback statistics."""

    product_id: uuid.UUID
    period_days: int
    total_count: int

    # Counts by dimension
    sentiment_counts: dict[str, int]
    category_counts: dict[str, int]
    source_counts: dict[str, int]
    urgency_counts: dict[str, int]

    # Churn metrics
    avg_churn_risk: float
    high_churn_count: int

    # Top phrases
    top_phrases: list[dict[str, Any]]

    # Trend data
    sentiment_trend: list[SentimentTrend]

    # Action metrics
    actioned_count: int
    actioned_rate: float


class FeedbackImportResponse(BaseSchema):
    """Schema for CSV import response."""

    imported: int
    failed: int
    errors: list[str] = Field(default_factory=list)


class FeedbackWebhookPayload(BaseSchema):
    """Schema for incoming webhook payload."""

    product_id: uuid.UUID
    text: str = Field(..., min_length=1, max_length=10000)
    source: str = Field(default="webhook", max_length=50)
    source_url: str | None = Field(None, max_length=500)
    author: str | None = Field(None, max_length=255)
    author_id: str | None = Field(None, max_length=255)
    analysis: dict[str, Any] | None = None  # Pre-analyzed data
    metadata: dict[str, Any] | None = None  # Extra metadata
