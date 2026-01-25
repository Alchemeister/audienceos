"""Phase 2: Add campaigns, generated posts, tracked links, and click events.

Revision ID: 002_campaigns_tracking
Revises: 001_initial
Create Date: 2025-01-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_campaigns_tracking"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Campaigns table
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="draft"),
        sa.Column("target_subreddits", postgresql.JSON, nullable=False, default=[]),
        sa.Column("total_clicks", sa.Integer, nullable=False, default=0),
        sa.Column("total_conversions", sa.Integer, nullable=False, default=0),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Create index for campaigns
    op.create_index(
        "ix_campaigns_product_status",
        "campaigns",
        ["product_id", "status"],
    )

    # Generated Posts table
    op.create_table(
        "generated_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("platform", sa.String(50), nullable=False, default="reddit"),
        sa.Column("target_community", sa.String(255), nullable=False),
        sa.Column("style", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("cta_subtle", sa.Text, nullable=True),
        sa.Column("estimated_engagement", sa.String(50), nullable=True),
        sa.Column("is_posted", sa.Boolean, nullable=False, default=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_url", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Tracked Links table
    op.create_table(
        "tracked_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("destination_url", sa.String(2000), nullable=False),
        sa.Column("short_code", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("utm_source", sa.String(100), nullable=False),
        sa.Column("utm_medium", sa.String(100), nullable=False, default="organic"),
        sa.Column("utm_campaign", sa.String(100), nullable=False),
        sa.Column("utm_content", sa.String(255), nullable=True),
        sa.Column("utm_term", sa.String(255), nullable=True),
        sa.Column("clicks", sa.Integer, nullable=False, default=0),
        sa.Column("conversions", sa.Integer, nullable=False, default=0),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Click Events table
    op.create_table(
        "click_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "link_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tracked_links.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("referer", sa.String(2000), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("converted", sa.Boolean, nullable=False, default=False),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("conversion_value", sa.Float, nullable=True),
    )

    # Create index for click events analytics
    op.create_index(
        "ix_click_events_link_clicked",
        "click_events",
        ["link_id", "clicked_at"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_click_events_link_clicked", table_name="click_events")
    op.drop_index("ix_campaigns_product_status", table_name="campaigns")

    # Drop tables in reverse order
    op.drop_table("click_events")
    op.drop_table("tracked_links")
    op.drop_table("generated_posts")
    op.drop_table("campaigns")
