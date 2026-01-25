"""Audience research endpoints (stub for Phase 1)."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import AIRouterDep, AsyncSessionDep, CurrentUserDep
from app.models.audience import AudienceResearch, AudienceSource, Platform
from app.models.product import Product
from app.schemas.audience import (
    AudienceResearchListResponse,
    AudienceResearchRequest,
    AudienceResearchResponse,
    AudienceSourceResponse,
)

router = APIRouter(prefix="/audiences", tags=["audiences"])


@router.post("/research", response_model=AudienceResearchResponse)
async def start_research(
    product_id: uuid.UUID,
    data: AudienceResearchRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    ai_router: AIRouterDep,
) -> AudienceResearchResponse:
    """
    Start audience research for a product.

    Uses AI to analyze the product description and find relevant
    subreddits, keywords, and competitors.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    # Verify product ownership
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

    # Use AI to research audience (EXPENSIVE tier)
    ai_result = await ai_router.research_audience(
        product_description=data.product_description,
    )

    # Create research record
    research = AudienceResearch(
        product_id=product_id,
        keywords=ai_result.get("keywords", []),
        competitors_mentioned=ai_result.get("competitors", []),
        confidence="high" if len(ai_result.get("subreddits", [])) >= 5 else "medium",
    )
    db.add(research)
    await db.flush()

    # Create audience sources from AI results
    sources = []
    for idx, subreddit_data in enumerate(ai_result.get("subreddits", [])[:10]):
        source = AudienceSource(
            product_id=product_id,
            research_id=research.id,
            platform=Platform.REDDIT,
            name=subreddit_data.get("name", f"r/unknown_{idx}"),
            url=f"https://reddit.com/{subreddit_data.get('name', '')}",
            relevance_score=subreddit_data.get("relevance_score", 0.5),
            reasoning=subreddit_data.get("reasoning", ""),
            recent_relevant_posts=0,
        )
        db.add(source)
        sources.append(source)

    await db.commit()
    await db.refresh(research)

    # Build response
    return AudienceResearchResponse(
        id=research.id,
        product_id=research.product_id,
        sources=[AudienceSourceResponse.model_validate(s) for s in sources],
        keywords=research.keywords,
        competitors_mentioned=research.competitors_mentioned,
        confidence=research.confidence,
        created_at=research.created_at,
    )


@router.get("/{research_id}", response_model=AudienceResearchResponse)
async def get_research(
    research_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> AudienceResearchResponse:
    """
    Get a specific audience research result.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    # Get research with sources
    result = await db.execute(
        select(AudienceResearch)
        .join(Product)
        .where(
            AudienceResearch.id == research_id,
            Product.organization_id == org_id,
        )
    )
    research = result.scalar_one_or_none()

    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found",
        )

    # Get sources
    sources_result = await db.execute(
        select(AudienceSource).where(AudienceSource.research_id == research_id)
    )
    sources = sources_result.scalars().all()

    return AudienceResearchResponse(
        id=research.id,
        product_id=research.product_id,
        sources=[AudienceSourceResponse.model_validate(s) for s in sources],
        keywords=research.keywords,
        competitors_mentioned=research.competitors_mentioned,
        confidence=research.confidence,
        created_at=research.created_at,
    )


@router.get("", response_model=AudienceResearchListResponse)
async def list_researches(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    limit: int = 10,
    offset: int = 0,
) -> AudienceResearchListResponse:
    """
    List all audience researches for a product.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    # Verify product ownership
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == org_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Get researches
    result = await db.execute(
        select(AudienceResearch)
        .where(AudienceResearch.product_id == product_id)
        .order_by(AudienceResearch.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    researches = result.scalars().all()

    # Get sources for each research
    items = []
    for research in researches:
        sources_result = await db.execute(
            select(AudienceSource).where(AudienceSource.research_id == research.id)
        )
        sources = sources_result.scalars().all()

        items.append(
            AudienceResearchResponse(
                id=research.id,
                product_id=research.product_id,
                sources=[AudienceSourceResponse.model_validate(s) for s in sources],
                keywords=research.keywords,
                competitors_mentioned=research.competitors_mentioned,
                confidence=research.confidence,
                created_at=research.created_at,
            )
        )

    # Count total
    count_result = await db.execute(
        select(AudienceResearch).where(AudienceResearch.product_id == product_id)
    )
    total = len(count_result.scalars().all())

    return AudienceResearchListResponse(items=items, total=total)
