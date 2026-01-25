"""User and Organization schemas."""

import uuid
from datetime import datetime

from app.schemas.common import BaseSchema, SubscriptionTier


class OrganizationBase(BaseSchema):
    """Base organization schema."""

    name: str


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""

    subscription_tier: SubscriptionTier = SubscriptionTier.INDIE


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    id: uuid.UUID
    subscription_tier: SubscriptionTier
    created_at: datetime
    updated_at: datetime


class UserBase(BaseSchema):
    """Base user schema."""

    email: str
    name: str


class UserCreate(UserBase):
    """Schema for creating a user."""

    clerk_id: str
    organization_id: uuid.UUID


class UserResponse(UserBase):
    """Schema for user response."""

    id: uuid.UUID
    clerk_id: str
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    organization: OrganizationResponse | None = None
