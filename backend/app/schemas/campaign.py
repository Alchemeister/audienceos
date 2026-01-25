"""Campaign, GeneratedPost, and TrackedLink schemas."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import Field, HttpUrl, field_validator

from app.schemas.common import BaseSchema, Platform, PostStyle


class CampaignStatus(str, Enum):
    """Campaign status."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# =============================================================================
# Campaign Schemas
# =============================================================================


class CampaignBase(BaseSchema):
    """Base campaign schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    target_subreddits: list[str] = Field(default_factory=list)


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""

    product_id: uuid.UUID


class CampaignUpdate(BaseSchema):
    """Schema for updating a campaign."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    status: CampaignStatus | None = None
    target_subreddits: list[str] | None = None


class GeneratedPostResponse(BaseSchema):
    """Schema for generated post response."""

    id: uuid.UUID
    campaign_id: uuid.UUID
    platform: str
    target_community: str
    style: str
    title: str | None
    body: str
    cta_subtle: str | None
    estimated_engagement: str | None
    is_posted: bool
    posted_at: datetime | None
    post_url: str | None
    created_at: datetime


class TrackedLinkResponse(BaseSchema):
    """Schema for tracked link response."""

    id: uuid.UUID
    campaign_id: uuid.UUID
    destination_url: str
    short_code: str
    short_url: str  # Computed
    utm_url: str  # Computed
    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_content: str | None
    utm_term: str | None
    clicks: int
    conversions: int
    conversion_rate: float
    created_at: datetime


class CampaignResponse(CampaignBase):
    """Schema for campaign response."""

    id: uuid.UUID
    product_id: uuid.UUID
    status: CampaignStatus
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    posts: list[GeneratedPostResponse] = Field(default_factory=list)
    links: list[TrackedLinkResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class CampaignListResponse(BaseSchema):
    """Schema for listing campaigns."""

    items: list[CampaignResponse]
    total: int


class CampaignStatsResponse(BaseSchema):
    """Schema for campaign statistics."""

    campaign_id: uuid.UUID
    campaign_name: str
    status: CampaignStatus
    total_posts: int
    total_links: int
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    clicks_by_source: dict[str, int]
    conversions_by_source: dict[str, int]
    top_performing_links: list[TrackedLinkResponse]
    recent_clicks: int  # Last 24 hours
    recent_conversions: int  # Last 24 hours


# =============================================================================
# Content Generation Schemas
# =============================================================================


class ContentGenerateRequest(BaseSchema):
    """Schema for content generation request."""

    subreddit: str = Field(..., min_length=1, max_length=100)
    topic_hint: str | None = Field(None, max_length=500)
    include_rules: bool = Field(default=True, description="Fetch and consider subreddit rules")


class GeneratedPostCreate(BaseSchema):
    """Schema for a single generated post."""

    style: PostStyle
    title: str | None = Field(None, max_length=500)
    body: str = Field(..., min_length=1)
    cta_subtle: str | None = None
    estimated_engagement: str | None = None


class ContentGenerateResponse(BaseSchema):
    """Schema for content generation response."""

    campaign_id: uuid.UUID
    subreddit: str
    subreddit_rules: list[str] | None
    posts: list[GeneratedPostResponse]


# =============================================================================
# Link Tracking Schemas
# =============================================================================


class TrackedLinkCreate(BaseSchema):
    """Schema for creating a tracked link."""

    campaign_id: uuid.UUID
    destination_url: str = Field(..., max_length=2000)
    utm_source: str = Field(..., min_length=1, max_length=100)
    utm_medium: str = Field(default="organic", max_length=100)
    utm_content: str | None = Field(None, max_length=255)
    utm_term: str | None = Field(None, max_length=255)

    @field_validator("destination_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate destination URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class TrackedLinkListResponse(BaseSchema):
    """Schema for listing tracked links."""

    items: list[TrackedLinkResponse]
    total: int


class ConversionRecord(BaseSchema):
    """Schema for recording a conversion."""

    short_code: str = Field(..., min_length=1, max_length=20)
    conversion_value: float | None = Field(None, ge=0)
    metadata: dict | None = None


class ConversionResponse(BaseSchema):
    """Schema for conversion recording response."""

    success: bool
    link_id: uuid.UUID
    campaign_id: uuid.UUID
    total_conversions: int


class ClickEventResponse(BaseSchema):
    """Schema for click event."""

    id: uuid.UUID
    link_id: uuid.UUID
    clicked_at: datetime
    country: str | None
    converted: bool
    converted_at: datetime | None
    conversion_value: float | None


class TrackingStatsResponse(BaseSchema):
    """Schema for overall tracking statistics."""

    total_links: int
    total_clicks: int
    total_conversions: int
    overall_conversion_rate: float
    clicks_today: int
    conversions_today: int
    top_campaigns: list[dict]
