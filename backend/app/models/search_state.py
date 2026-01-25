"""Search state models for tracking incremental feedback collection."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Product


class KeywordSearchState(Base, UUIDMixin):
    """
    Tracks the search state for each keyword/platform combination.

    This enables incremental searching - instead of searching the entire
    history every time, we only search from the last successful search.

    Example:
        - keyword: "hims"
        - platform: "reddit"
        - last_searched_at: 2024-01-20 10:00:00
        - last_content_at: 2024-01-20 08:30:00 (newest content found)

        Next search will only look for content after 2024-01-20 08:30:00
    """

    __tablename__ = "keyword_search_states"

    product_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # reddit, twitter, hackernews, etc.

    # When we last ran a search for this keyword/platform
    last_searched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamp of the newest content found in last search
    # Next search starts from here to avoid duplicates
    last_content_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # When the next search should run (for scheduling)
    next_search_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Stats for monitoring
    total_items_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_search_items_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consecutive_empty_searches: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Error tracking
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_error_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="keyword_search_states")

    __table_args__ = (
        # Each keyword/platform combo is unique per product
        UniqueConstraint("product_id", "keyword", "platform", name="uq_product_keyword_platform"),
        # Index for finding keywords due for search
        Index("ix_keyword_search_next", "next_search_at"),
    )

    def mark_search_complete(
        self,
        items_found: int,
        newest_content_at: datetime | None = None,
        next_search_hours: int = 24,
    ) -> None:
        """
        Mark a search as complete and schedule the next one.

        Args:
            items_found: Number of new items found in this search
            newest_content_at: Timestamp of the newest content found
            next_search_hours: Hours until next scheduled search
        """
        from datetime import timedelta

        self.last_searched_at = datetime.utcnow()
        self.last_search_items_found = items_found
        self.total_items_found += items_found
        self.last_error = None
        self.last_error_at = None

        if items_found > 0:
            self.consecutive_empty_searches = 0
            if newest_content_at:
                self.last_content_at = newest_content_at
        else:
            self.consecutive_empty_searches += 1

        # Adaptive scheduling: search less frequently if no results
        if self.consecutive_empty_searches >= 5:
            # After 5 empty searches, slow down to every 3 days
            next_search_hours = 72
        elif self.consecutive_empty_searches >= 3:
            # After 3 empty searches, slow down to every 2 days
            next_search_hours = 48

        self.next_search_at = datetime.utcnow() + timedelta(hours=next_search_hours)

    def mark_search_error(self, error_message: str) -> None:
        """Mark a search as failed with an error."""
        from datetime import timedelta

        self.last_error = error_message[:500]
        self.last_error_at = datetime.utcnow()
        # Retry sooner on error (1 hour)
        self.next_search_at = datetime.utcnow() + timedelta(hours=1)
