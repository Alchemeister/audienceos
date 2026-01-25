"""Phase 5B: Add billing infrastructure tables.

Revision ID: 003_billing
Revises: 002_campaigns_tracking
Create Date: 2025-01-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_billing"
down_revision: Union[str, None] = "002_campaigns_tracking"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("tier", sa.String(50), nullable=False, default="indie"),
        sa.Column("status", sa.String(50), nullable=False, default="active"),
        sa.Column(
            "current_period_start",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "current_period_end",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("cancel_at_period_end", sa.Boolean, nullable=False, default=False),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True, unique=True),
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

    # Create indexes for subscriptions
    op.create_index(
        "ix_subscriptions_organization_id",
        "subscriptions",
        ["organization_id"],
    )
    op.create_index(
        "ix_subscriptions_stripe_subscription_id",
        "subscriptions",
        ["stripe_subscription_id"],
    )
    op.create_index(
        "ix_subscriptions_status",
        "subscriptions",
        ["status"],
    )

    # Usage Records table
    op.create_table(
        "usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "period_start",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "period_end",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("feedback_count", sa.Integer, nullable=False, default=0),
        sa.Column("keywords_count", sa.Integer, nullable=False, default=0),
        sa.Column("deep_analysis_used", sa.Integer, nullable=False, default=0),
        sa.Column("products_count", sa.Integer, nullable=False, default=0),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Create indexes for usage records
    op.create_index(
        "ix_usage_records_organization_id",
        "usage_records",
        ["organization_id"],
    )
    op.create_index(
        "ix_usage_records_org_period",
        "usage_records",
        ["organization_id", "period_start"],
    )

    # Billing Events table
    op.create_table(
        "billing_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Create indexes for billing events
    op.create_index(
        "ix_billing_events_organization_id",
        "billing_events",
        ["organization_id"],
    )
    op.create_index(
        "ix_billing_events_org_type",
        "billing_events",
        ["organization_id", "event_type"],
    )
    op.create_index(
        "ix_billing_events_created",
        "billing_events",
        ["created_at"],
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_billing_events_created", table_name="billing_events")
    op.drop_index("ix_billing_events_org_type", table_name="billing_events")
    op.drop_index("ix_billing_events_organization_id", table_name="billing_events")
    op.drop_index("ix_usage_records_org_period", table_name="usage_records")
    op.drop_index("ix_usage_records_organization_id", table_name="usage_records")
    op.drop_index("ix_subscriptions_status", table_name="subscriptions")
    op.drop_index("ix_subscriptions_stripe_subscription_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_organization_id", table_name="subscriptions")

    # Drop tables in reverse order
    op.drop_table("billing_events")
    op.drop_table("usage_records")
    op.drop_table("subscriptions")
