"""Product schemas."""

import uuid
from datetime import datetime

from pydantic import Field, HttpUrl

from app.schemas.common import BaseSchema


class ProductBase(BaseSchema):
    """Base product schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    url: str | None = Field(None, max_length=500)


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    keywords: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)


class ProductUpdate(BaseSchema):
    """Schema for updating a product."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    url: str | None = Field(None, max_length=500)
    keywords: list[str] | None = None
    competitors: list[str] | None = None


class ProductResponse(ProductBase):
    """Schema for product response."""

    id: uuid.UUID
    organization_id: uuid.UUID
    keywords: list[str]
    competitors: list[str]
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseSchema):
    """Schema for listing products."""

    items: list[ProductResponse]
    total: int
