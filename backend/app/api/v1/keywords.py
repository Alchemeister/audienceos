"""API endpoints for keyword management."""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.services.keywords import KeywordGenerationService
from app.tasks.keywords import generate_keywords_for_product

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{product_id}/generate")
async def generate_product_keywords(
    product_id: UUID,
    force_regenerate: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Generate keywords for a product using AI.

    This endpoint:
    1. Uses AI to discover relevant keywords based on product description
    2. Categorizes keywords (brand, competitors, problems, solutions)
    3. Filters by confidence score
    4. Updates the product's keyword list

    **Caching:** Results are cached for 7 days to save on AI costs.

    **Arguments:**
    - force_regenerate: If true, ignores cache and existing keywords
    """
    # Get product and verify ownership
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or access denied",
        )

    # Queue keyword generation task
    task = generate_keywords_for_product.delay(
        str(product_id),
        force_regenerate=force_regenerate,
    )

    return {
        "message": "Keyword generation started",
        "task_id": task.id,
        "product_id": str(product_id),
        "product_name": product.name,
    }


@router.get("/{product_id}/keywords")
async def get_product_keywords(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get current keywords for a product."""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or access denied",
        )

    return {
        "product_id": str(product.id),
        "product_name": product.name,
        "keywords": product.keywords,
        "keyword_count": len(product.keywords),
        "competitors": product.competitors,
    }


@router.put("/{product_id}/keywords")
async def update_product_keywords(
    product_id: UUID,
    add_keywords: list[str] | None = None,
    remove_keywords: list[str] | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Manually update product keywords.

    **Arguments:**
    - add_keywords: List of keywords to add
    - remove_keywords: List of keywords to remove
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or access denied",
        )

    service = KeywordGenerationService()
    update_result = await service.update_keywords_for_product(
        db, product, add_keywords, remove_keywords
    )

    return update_result


@router.get("/{product_id}/keywords/analyze")
async def analyze_keyword_coverage(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Analyze keyword coverage and get recommendations.

    Returns analysis of current keyword coverage with suggestions
    for improvement.
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or access denied",
        )

    service = KeywordGenerationService()
    analysis = await service.analyze_keyword_coverage(product)

    return analysis
