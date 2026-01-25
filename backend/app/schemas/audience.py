"""Audience research schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import BaseSchema, Platform


class AudienceSourceResponse(BaseSchema):
    """Schema for audience source response."""

    id: uuid.UUID
    product_id: uuid.UUID
    platform: Platform
    name: str
    url: str
    relevance_score: float = Field(..., ge=0, le=1)
    monthly_active: int | None
    recent_relevant_posts: int
    reasoning: str
    discovered_at: datetime
    last_checked: datetime


class AudienceResearchRequest(BaseSchema):
    """Schema for starting audience research."""

    product_description: str = Field(..., min_length=10)
    product_url: str | None = None
    focus: Literal["b2b", "b2c", "developer"] | None = None


class AudienceResearchResponse(BaseSchema):
    """Schema for audience research results."""

    id: uuid.UUID
    product_id: uuid.UUID
    sources: list[AudienceSourceResponse]
    keywords: list[str]
    competitors_mentioned: list[str]
    confidence: Literal["low", "medium", "high"]
    created_at: datetime


class AudienceResearchListResponse(BaseSchema):
    """Schema for listing audience researches."""

    items: list[AudienceResearchResponse]
    total: int
