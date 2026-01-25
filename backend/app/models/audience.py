"""Audience research models."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Product


class Platform(str, Enum):
    """Supported platforms for audience research and feedback."""

    REDDIT = "reddit"
    TWITTER = "twitter"
    HACKERNEWS = "hackernews"
    GITHUB = "github"
    EMAIL = "email"
    WIDGET = "widget"
    MANUAL = "manual"


class AudienceSource(Base, UUIDMixin):
    """A discovered audience location (e.g., a subreddit)."""

    __tablename__ = "audience_sources"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    research_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("audience_researches.id", ondelete="SET NULL"),
        nullable=True,
    )
    platform: Mapped[Platform] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "r/SaaS"
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_active: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recent_relevant_posts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_checked: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", back_populates="audience_sources"
    )
    research: Mapped["AudienceResearch | None"] = relationship(
        "AudienceResearch", back_populates="sources"
    )


class AudienceResearch(Base, UUIDMixin):
    """Results of an audience research session."""

    __tablename__ = "audience_researches"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    competitors_mentioned: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    confidence: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # low, medium, high
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product", back_populates="audience_researches"
    )
    sources: Mapped[list["AudienceSource"]] = relationship(
        "AudienceSource", back_populates="research"
    )
