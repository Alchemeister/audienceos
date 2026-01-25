"""Common schemas and enums used across the application."""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


# Re-export enums from models for API use
class Platform(str, Enum):
    """Supported platforms for audience research and feedback."""

    REDDIT = "reddit"
    TWITTER = "twitter"
    HACKERNEWS = "hackernews"
    GITHUB = "github"
    EMAIL = "email"
    WIDGET = "widget"
    MANUAL = "manual"


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


class PostStyle(str, Enum):
    """Content post style."""

    HELPFUL = "helpful"
    STORY = "story"
    QUESTION = "question"
    INSIGHT = "insight"


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""

    INDIE = "indie"
    PRO = "pro"
    AGENCY = "agency"


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str
    version: str = "1.0.0"


class ErrorResponse(BaseSchema):
    """Standard error response."""

    error: str
    message: str
    details: dict | None = None
