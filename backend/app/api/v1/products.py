"""Product CRUD endpoints."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import (
    AIRouterDep,
    AsyncSessionDep,
    CurrentUserDep,
    UsageServiceDep,
    check_product_limit,
)
from app.models.product import Product
from app.models.user import Organization
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_product_limit)],
)
async def create_product(
    data: ProductCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    usage_service: UsageServiceDep,
) -> ProductResponse:
    """
    Create a new product to track.

    The product will be associated with the user's organization.
    """
    # Get or create organization (for development)
    org_id = uuid.UUID(current_user["organization_id"])

    # Check if organization exists
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()

    if not org:
        # Create organization for development
        org = Organization(
            id=org_id,
            name="Development Org",
        )
        db.add(org)
        await db.flush()

    # Create product
    product = Product(
        organization_id=org_id,
        name=data.name,
        description=data.description,
        url=data.url,
        keywords=data.keywords,
        competitors=data.competitors,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    # Update usage tracking
    await usage_service.increment_usage(org_id, "products")

    # Trigger historical backfill in background
    try:
        from app.tasks.feedback import trigger_backfill_for_new_product

        trigger_backfill_for_new_product.delay(str(product.id))
        logger.info(f"Queued backfill task for product {product.id}")
    except Exception as e:
        # Don't fail product creation if Celery isn't running
        logger.warning(f"Could not queue backfill task: {e}")

    return ProductResponse.model_validate(product)


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    limit: int = 50,
    offset: int = 0,
) -> ProductListResponse:
    """
    List all products for the current organization.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    # Get products
    result = await db.execute(
        select(Product)
        .where(Product.organization_id == org_id)
        .order_by(Product.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    products = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(Product).where(Product.organization_id == org_id)
    )
    total = len(count_result.scalars().all())

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> ProductResponse:
    """
    Get a specific product by ID.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == org_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> ProductResponse:
    """
    Update a product.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == org_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete a product.

    This will also delete all associated audience sources, researches, and feedback.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == org_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    await db.delete(product)
    await db.commit()
