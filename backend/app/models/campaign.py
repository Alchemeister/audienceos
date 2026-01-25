"""Campaign, GeneratedPost, and TrackedLink models."""

import secrets
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Product


class CampaignStatus(str, PyEnum):
    """Campaign status enum."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PostStyle(str, PyEnum):
    """Content post style enum."""

    HELPFUL = "helpful"
    STORY = "story"
    QUESTION = "question"
    INSIGHT = "insight"


class Campaign(Base, UUIDMixin, TimestampMixin):
    """A marketing campaign (set of posts + tracking)."""

    __tablename__ = "campaigns"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default=CampaignStatus.DRAFT.value,
        nullable=False,
    )
    target_subreddits: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    total_clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_conversions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="campaigns")
    posts: Mapped[list["GeneratedPost"]] = relationship(
        "GeneratedPost", back_populates="campaign", cascade="all, delete-orphan"
    )
    links: Mapped[list["TrackedLink"]] = relationship(
        "TrackedLink", back_populates="campaign", cascade="all, delete-orphan"
    )

    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        if self.total_clicks == 0:
            return 0.0
        return round(self.total_conversions / self.total_clicks * 100, 2)

    # Indexes
    __table_args__ = (
        Index("ix_campaigns_product_status", "product_id", "status"),
    )


class GeneratedPost(Base, UUIDMixin, TimestampMixin):
    """AI-generated post content."""

    __tablename__ = "generated_posts"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False, default="reddit")
    target_community: Mapped[str] = mapped_column(String(255), nullable=False)
    style: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    cta_subtle: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_engagement: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Tracking (if posted)
    is_posted: Mapped[bool] = mapped_column(default=False, nullable=False)
    posted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    post_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="posts")


def generate_short_code(length: int = 7) -> str:
    """Generate a URL-safe short code."""
    # Use URL-safe characters: a-z, A-Z, 0-9
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


class TrackedLink(Base, UUIDMixin, TimestampMixin):
    """A trackable link for conversion attribution."""

    __tablename__ = "tracked_links"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    destination_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    short_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        default=generate_short_code,
        index=True,
    )

    # UTM Parameters
    utm_source: Mapped[str] = mapped_column(String(100), nullable=False)
    utm_medium: Mapped[str] = mapped_column(String(100), nullable=False, default="organic")
    utm_campaign: Mapped[str] = mapped_column(String(100), nullable=False)
    utm_content: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_term: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metrics
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conversions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="links")
    click_events: Mapped[list["ClickEvent"]] = relationship(
        "ClickEvent", back_populates="link", cascade="all, delete-orphan"
    )

    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        if self.clicks == 0:
            return 0.0
        return round(self.conversions / self.clicks * 100, 2)

    def build_utm_url(self) -> str:
        """Build the full URL with UTM parameters."""
        from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

        parsed = urlparse(self.destination_url)
        params = parse_qs(parsed.query)

        # Add UTM params
        params["utm_source"] = [self.utm_source]
        params["utm_medium"] = [self.utm_medium]
        params["utm_campaign"] = [self.utm_campaign]
        if self.utm_content:
            params["utm_content"] = [self.utm_content]
        if self.utm_term:
            params["utm_term"] = [self.utm_term]

        # Rebuild URL
        new_query = urlencode({k: v[0] for k, v in params.items()})
        return urlunparse(parsed._replace(query=new_query))


class ClickEvent(Base, UUIDMixin):
    """Individual click tracking event."""

    __tablename__ = "click_events"

    link_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("tracked_links.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clicked_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Hashed for privacy
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    referer: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)  # ISO country code

    # Conversion tracking
    converted: Mapped[bool] = mapped_column(default=False, nullable=False)
    converted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    conversion_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    link: Mapped["TrackedLink"] = relationship("TrackedLink", back_populates="click_events")

    # Indexes for analytics
    __table_args__ = (
        Index("ix_click_events_link_clicked", "link_id", "clicked_at"),
    )
