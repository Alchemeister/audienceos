"""Campaign CRUD and content generation endpoints."""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import AIRouterDep, AsyncSessionDep, CurrentUserDep, SettingsDep
from app.core.config import get_settings
from app.models.campaign import Campaign, GeneratedPost, TrackedLink, ClickEvent
from app.models.product import Product
from app.schemas.campaign import (
    CampaignCreate,
    CampaignListResponse,
    CampaignResponse,
    CampaignStatsResponse,
    CampaignUpdate,
    ContentGenerateRequest,
    ContentGenerateResponse,
    GeneratedPostResponse,
    TrackedLinkResponse,
)
from app.services.research.reddit import RedditClient

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _build_tracked_link_response(link: TrackedLink, base_url: str) -> TrackedLinkResponse:
    """Helper to build TrackedLinkResponse with computed fields."""
    return TrackedLinkResponse(
        id=link.id,
        campaign_id=link.campaign_id,
        destination_url=link.destination_url,
        short_code=link.short_code,
        short_url=f"{base_url}/aos/{link.short_code}",
        utm_url=link.build_utm_url(),
        utm_source=link.utm_source,
        utm_medium=link.utm_medium,
        utm_campaign=link.utm_campaign,
        utm_content=link.utm_content,
        utm_term=link.utm_term,
        clicks=link.clicks,
        conversions=link.conversions,
        conversion_rate=link.conversion_rate,
        created_at=link.created_at,
    )


def _build_campaign_response(campaign: Campaign, base_url: str) -> CampaignResponse:
    """Helper to build CampaignResponse with related data."""
    posts = [
        GeneratedPostResponse(
            id=post.id,
            campaign_id=post.campaign_id,
            platform=post.platform,
            target_community=post.target_community,
            style=post.style,
            title=post.title,
            body=post.body,
            cta_subtle=post.cta_subtle,
            estimated_engagement=post.estimated_engagement,
            is_posted=post.is_posted,
            posted_at=post.posted_at,
            post_url=post.post_url,
            created_at=post.created_at,
        )
        for post in campaign.posts
    ]

    links = [_build_tracked_link_response(link, base_url) for link in campaign.links]

    return CampaignResponse(
        id=campaign.id,
        product_id=campaign.product_id,
        name=campaign.name,
        description=campaign.description,
        status=campaign.status,
        target_subreddits=campaign.target_subreddits,
        total_clicks=campaign.total_clicks,
        total_conversions=campaign.total_conversions,
        conversion_rate=campaign.conversion_rate,
        posts=posts,
        links=links,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> CampaignResponse:
    """
    Create a new campaign for a product.

    The campaign will be created in draft status.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    settings = get_settings()

    # Verify product exists and belongs to organization
    result = await db.execute(
        select(Product).where(
            Product.id == data.product_id,
            Product.organization_id == org_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Create campaign
    campaign = Campaign(
        product_id=data.product_id,
        name=data.name,
        description=data.description,
        target_subreddits=data.target_subreddits,
        status="draft",
    )
    db.add(campaign)
    await db.flush()  # Get the ID
    await db.refresh(campaign)

    # Return response directly - new campaign has no posts/links
    response = CampaignResponse(
        id=campaign.id,
        product_id=campaign.product_id,
        name=campaign.name,
        description=campaign.description,
        status=campaign.status,
        target_subreddits=campaign.target_subreddits,
        total_clicks=0,
        total_conversions=0,
        conversion_rate=0.0,
        posts=[],
        links=[],
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )

    await db.commit()
    return response


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    product_id: uuid.UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> CampaignListResponse:
    """
    List campaigns for the current organization.

    Optionally filter by product_id or status.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    settings = get_settings()

    # Build query with filters
    query = (
        select(Campaign)
        .join(Product)
        .where(Product.organization_id == org_id)
        .options(selectinload(Campaign.posts), selectinload(Campaign.links))
    )

    if product_id:
        query = query.where(Campaign.product_id == product_id)
    if status:
        query = query.where(Campaign.status == status)

    query = query.order_by(Campaign.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    campaigns = result.scalars().all()

    # Get total count
    count_query = select(func.count(Campaign.id)).join(Product).where(Product.organization_id == org_id)
    if product_id:
        count_query = count_query.where(Campaign.product_id == product_id)
    if status:
        count_query = count_query.where(Campaign.status == status)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return CampaignListResponse(
        items=[_build_campaign_response(c, settings.APP_URL) for c in campaigns],
        total=total,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> CampaignResponse:
    """
    Get a specific campaign by ID.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    settings = get_settings()

    result = await db.execute(
        select(Campaign)
        .join(Product)
        .where(
            Campaign.id == campaign_id,
            Product.organization_id == org_id,
        )
        .options(selectinload(Campaign.posts), selectinload(Campaign.links))
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    return _build_campaign_response(campaign, settings.APP_URL)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    data: CampaignUpdate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> CampaignResponse:
    """
    Update a campaign.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    settings = get_settings()

    result = await db.execute(
        select(Campaign)
        .join(Product)
        .where(
            Campaign.id == campaign_id,
            Product.organization_id == org_id,
        )
        .options(selectinload(Campaign.posts), selectinload(Campaign.links))
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value:
            value = value.value if hasattr(value, "value") else value
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)

    return _build_campaign_response(campaign, settings.APP_URL)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> None:
    """
    Delete a campaign.

    This will also delete all associated posts and tracked links.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(Campaign)
        .join(Product)
        .where(
            Campaign.id == campaign_id,
            Product.organization_id == org_id,
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    await db.delete(campaign)
    await db.commit()


@router.post("/{campaign_id}/generate", response_model=ContentGenerateResponse)
async def generate_content(
    campaign_id: uuid.UUID,
    data: ContentGenerateRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    ai_router: AIRouterDep,
    settings: SettingsDep,
) -> ContentGenerateResponse:
    """
    Generate content posts for a campaign using AI.

    Uses the EXPENSIVE tier AI (Claude) to generate 3 post styles:
    - helpful: Share a tip, insight, or solution
    - story: Share a relatable experience or lesson learned
    - question: Ask a thought-provoking question

    If include_rules is True (default), fetches subreddit rules to guide generation.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    # Get campaign with product
    result = await db.execute(
        select(Campaign)
        .join(Product)
        .where(
            Campaign.id == campaign_id,
            Product.organization_id == org_id,
        )
        .options(selectinload(Campaign.product))
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    product = campaign.product

    # Clean subreddit name (remove r/ prefix if present)
    subreddit = data.subreddit.lstrip("r/").strip()

    # Fetch subreddit rules if requested
    rules_text = "No specific rules provided."
    rules_list = None

    if data.include_rules:
        try:
            reddit = RedditClient(settings)
            rules_text = await reddit.get_subreddit_rules_text(subreddit)
            rules = await reddit.get_subreddit_rules(subreddit)
            rules_list = [r.get("short_name", "") for r in rules if r.get("short_name")]
            await reddit.close()
        except Exception:
            # Don't fail if rules can't be fetched
            rules_text = "Could not fetch rules. Follow general Reddit etiquette."

    # Build topic from hint or product keywords
    topic = data.topic_hint or ", ".join(product.keywords[:5]) if product.keywords else product.name

    # Build product context (AI uses this but doesn't mention it directly)
    product_context = f"{product.name}: {product.description}"

    # Generate content using AI (EXPENSIVE tier)
    ai_result = await ai_router.generate_content(
        subreddit=f"r/{subreddit}",
        rules=rules_text,
        topic=topic,
        product_context=product_context,
    )

    # Save generated posts to database
    generated_posts = []
    for post_data in ai_result.get("posts", []):
        post = GeneratedPost(
            campaign_id=campaign.id,
            platform="reddit",
            target_community=f"r/{subreddit}",
            style=post_data.get("style", "helpful"),
            title=post_data.get("title"),
            body=post_data.get("body", ""),
            cta_subtle=post_data.get("cta_subtle"),
            estimated_engagement=post_data.get("estimated_engagement"),
        )
        db.add(post)
        generated_posts.append(post)

    # Update campaign target_subreddits if not already included
    if subreddit not in campaign.target_subreddits:
        campaign.target_subreddits = campaign.target_subreddits + [subreddit]

    await db.commit()

    # Refresh posts to get IDs
    for post in generated_posts:
        await db.refresh(post)

    return ContentGenerateResponse(
        campaign_id=campaign.id,
        subreddit=f"r/{subreddit}",
        subreddit_rules=rules_list,
        posts=[
            GeneratedPostResponse(
                id=post.id,
                campaign_id=post.campaign_id,
                platform=post.platform,
                target_community=post.target_community,
                style=post.style,
                title=post.title,
                body=post.body,
                cta_subtle=post.cta_subtle,
                estimated_engagement=post.estimated_engagement,
                is_posted=post.is_posted,
                posted_at=post.posted_at,
                post_url=post.post_url,
                created_at=post.created_at,
            )
            for post in generated_posts
        ],
    )


@router.get("/{campaign_id}/stats", response_model=CampaignStatsResponse)
async def get_campaign_stats(
    campaign_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> CampaignStatsResponse:
    """
    Get detailed statistics for a campaign.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    settings = get_settings()
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)

    # Get campaign with all related data
    result = await db.execute(
        select(Campaign)
        .join(Product)
        .where(
            Campaign.id == campaign_id,
            Product.organization_id == org_id,
        )
        .options(
            selectinload(Campaign.posts),
            selectinload(Campaign.links).selectinload(TrackedLink.click_events),
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    # Calculate stats
    clicks_by_source: dict[str, int] = {}
    conversions_by_source: dict[str, int] = {}
    recent_clicks = 0
    recent_conversions = 0

    for link in campaign.links:
        source = link.utm_source
        clicks_by_source[source] = clicks_by_source.get(source, 0) + link.clicks
        conversions_by_source[source] = conversions_by_source.get(source, 0) + link.conversions

        # Count recent activity from click events
        for event in link.click_events:
            if event.clicked_at >= day_ago:
                recent_clicks += 1
                if event.converted:
                    recent_conversions += 1

    # Get top performing links (by conversion rate, min 5 clicks)
    top_links = sorted(
        [link for link in campaign.links if link.clicks >= 5],
        key=lambda x: x.conversion_rate,
        reverse=True,
    )[:5]

    return CampaignStatsResponse(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        status=campaign.status,
        total_posts=len(campaign.posts),
        total_links=len(campaign.links),
        total_clicks=campaign.total_clicks,
        total_conversions=campaign.total_conversions,
        conversion_rate=campaign.conversion_rate,
        clicks_by_source=clicks_by_source,
        conversions_by_source=conversions_by_source,
        top_performing_links=[_build_tracked_link_response(link, settings.APP_URL) for link in top_links],
        recent_clicks=recent_clicks,
        recent_conversions=recent_conversions,
    )
