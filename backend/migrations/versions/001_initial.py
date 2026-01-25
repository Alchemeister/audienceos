"""Initial migration - create all Phase 1 tables.

Revision ID: 001_initial
Revises:
Create Date: 2025-01-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Organizations table
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("subscription_tier", sa.String(50), nullable=False, default="indie"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
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

    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_id", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
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

    # Products table
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("keywords", postgresql.JSON, nullable=False, default=[]),
        sa.Column("competitors", postgresql.JSON, nullable=False, default=[]),
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

    # Audience Researches table
    op.create_table(
        "audience_researches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("keywords", postgresql.JSON, nullable=False, default=[]),
        sa.Column("competitors_mentioned", postgresql.JSON, nullable=False, default=[]),
        sa.Column("confidence", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Audience Sources table
    op.create_table(
        "audience_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "research_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("audience_researches.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("relevance_score", sa.Float, nullable=False),
        sa.Column("monthly_active", sa.Integer, nullable=True),
        sa.Column("recent_relevant_posts", sa.Integer, nullable=False, default=0),
        sa.Column("reasoning", sa.Text, nullable=False),
        sa.Column(
            "discovered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "last_checked",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Feedback Items table
    op.create_table(
        "feedback_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("author_id", sa.String(255), nullable=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("sentiment", sa.String(50), nullable=False),
        sa.Column("emotion", sa.String(100), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("urgency", sa.String(50), nullable=False, default="medium"),
        sa.Column("product_area", sa.String(255), nullable=True),
        sa.Column("key_phrases", postgresql.JSON, nullable=False, default=[]),
        sa.Column("churn_risk", sa.Float, nullable=False, default=0.0),
        sa.Column("suggested_action", sa.Text, nullable=True),
        sa.Column("is_actioned", sa.Boolean, nullable=False, default=False),
        sa.Column("actioned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_data", postgresql.JSON, nullable=False, default={}),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
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

    # Create indexes for feedback_items
    op.create_index(
        "ix_feedback_items_product_source",
        "feedback_items",
        ["product_id", "source"],
    )
    op.create_index(
        "ix_feedback_items_product_sentiment",
        "feedback_items",
        ["product_id", "sentiment"],
    )
    op.create_index(
        "ix_feedback_items_product_category",
        "feedback_items",
        ["product_id", "category"],
    )
    op.create_index(
        "ix_feedback_items_product_created",
        "feedback_items",
        ["product_id", "created_at"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_feedback_items_product_created", table_name="feedback_items")
    op.drop_index("ix_feedback_items_product_category", table_name="feedback_items")
    op.drop_index("ix_feedback_items_product_sentiment", table_name="feedback_items")
    op.drop_index("ix_feedback_items_product_source", table_name="feedback_items")

    # Drop tables in reverse order
    op.drop_table("feedback_items")
    op.drop_table("audience_sources")
    op.drop_table("audience_researches")
    op.drop_table("products")
    op.drop_table("users")
    op.drop_table("organizations")
