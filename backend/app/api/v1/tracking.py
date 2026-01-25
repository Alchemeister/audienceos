"""Link tracking and conversion endpoints."""

import hashlib
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import AsyncSessionDep, CurrentUserDep
from app.core.config import get_settings
from app.models.campaign import Campaign, ClickEvent, TrackedLink
from app.models.product import Product
from app.schemas.campaign import (
    ConversionRecord,
    ConversionResponse,
    TrackedLinkCreate,
    TrackedLinkListResponse,
    TrackedLinkResponse,
    TrackingStatsResponse,
)

router = APIRouter(tags=["tracking"])


def _hash_ip(ip: str) -> str:
    """Hash IP address for privacy-preserving storage."""
    # Use SHA-256 with a salt for privacy
    salt = get_settings().SECRET_KEY or "audienceos-salt"
    return hashlib.sha256(f"{salt}:{ip}".encode()).hexdigest()[:32]


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


@router.post("/api/v1/tracking/links", response_model=TrackedLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_tracked_link(
    data: TrackedLinkCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> TrackedLinkResponse:
    """
    Create a new tracked link with UTM parameters.

    The link will be associated with a campaign and generate:
    - A short URL for tracking clicks
    - A full URL with UTM parameters for analytics
    """
    org_id = uuid.UUID(current_user["organization_id"])
    settings = get_settings()

    # Verify campaign exists and belongs to organization
    result = await db.execute(
        select(Campaign)
        .join(Product)
        .where(
            Campaign.id == data.campaign_id,
            Product.organization_id == org_id,
        )
    )
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    # Create tracked link
    link = TrackedLink(
        campaign_id=data.campaign_id,
        destination_url=data.destination_url,
        utm_source=data.utm_source,
        utm_medium=data.utm_medium,
        utm_campaign=campaign.name.lower().replace(" ", "-"),
        utm_content=data.utm_content,
        utm_term=data.utm_term,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)

    return _build_tracked_link_response(link, settings.APP_URL)


@router.get("/api/v1/tracking/links", response_model=TrackedLinkListResponse)
async def list_tracked_links(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    campaign_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> TrackedLinkListResponse:
    """
    List tracked links for the current organization.

    Optionally filter by campaign_id.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    settings = get_settings()

    # Build query with filters
    query = (
        select(TrackedLink)
        .join(Campaign)
        .join(Product)
        .where(Product.organization_id == org_id)
    )

    if campaign_id:
        query = query.where(TrackedLink.campaign_id == campaign_id)

    query = query.order_by(TrackedLink.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    links = result.scalars().all()

    # Get total count
    count_query = (
        select(func.count(TrackedLink.id))
        .join(Campaign)
        .join(Product)
        .where(Product.organization_id == org_id)
    )
    if campaign_id:
        count_query = count_query.where(TrackedLink.campaign_id == campaign_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return TrackedLinkListResponse(
        items=[_build_tracked_link_response(link, settings.APP_URL) for link in links],
        total=total,
    )


@router.get("/aos/{short_code}")
async def redirect_tracked_link(
    short_code: str,
    request: Request,
    db: AsyncSessionDep,
) -> RedirectResponse:
    """
    Redirect endpoint for tracked links.

    Records the click with metadata for analytics, then redirects to the destination.
    This endpoint is public (no auth required) to allow click tracking.
    """
    # Find the link
    result = await db.execute(
        select(TrackedLink).where(TrackedLink.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    # Record click event
    client_ip = request.client.host if request.client else None
    ip_hash = _hash_ip(client_ip) if client_ip else None

    click_event = ClickEvent(
        link_id=link.id,
        clicked_at=datetime.utcnow(),
        ip_hash=ip_hash,
        user_agent=request.headers.get("user-agent", "")[:500],
        referer=request.headers.get("referer", "")[:2000] if request.headers.get("referer") else None,
    )
    db.add(click_event)

    # Increment click counter
    link.clicks += 1

    # Update campaign total clicks
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == link.campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    if campaign:
        campaign.total_clicks += 1

    await db.commit()

    # Build redirect URL with UTM params
    redirect_url = link.build_utm_url()

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post("/api/v1/tracking/convert", response_model=ConversionResponse)
async def record_conversion(
    data: ConversionRecord,
    db: AsyncSessionDep,
) -> ConversionResponse:
    """
    Record a conversion for a tracked link.

    This endpoint is typically called from a JavaScript snippet on the destination site
    or via a webhook from payment providers like Stripe.

    Public endpoint (no auth) to allow conversion tracking from client sites.
    """
    # Find the link
    result = await db.execute(
        select(TrackedLink)
        .where(TrackedLink.short_code == data.short_code)
        .options(selectinload(TrackedLink.click_events))
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    # Find the most recent unconverted click event (within last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_click = None

    for event in sorted(link.click_events, key=lambda x: x.clicked_at, reverse=True):
        if not event.converted and event.clicked_at >= thirty_days_ago:
            recent_click = event
            break

    # Mark click as converted if found
    if recent_click:
        recent_click.converted = True
        recent_click.converted_at = datetime.utcnow()
        recent_click.conversion_value = data.conversion_value

    # Increment conversion counters
    link.conversions += 1

    # Update campaign total conversions
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == link.campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    if campaign:
        campaign.total_conversions += 1

    await db.commit()

    return ConversionResponse(
        success=True,
        link_id=link.id,
        campaign_id=link.campaign_id,
        total_conversions=link.conversions,
    )


@router.get("/api/v1/tracking/stats", response_model=TrackingStatsResponse)
async def get_tracking_stats(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> TrackingStatsResponse:
    """
    Get overall tracking statistics for the organization.
    """
    org_id = uuid.UUID(current_user["organization_id"])
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)

    # Get all links for the organization
    result = await db.execute(
        select(TrackedLink)
        .join(Campaign)
        .join(Product)
        .where(Product.organization_id == org_id)
        .options(selectinload(TrackedLink.click_events))
    )
    links = result.scalars().all()

    # Calculate stats
    total_links = len(links)
    total_clicks = sum(link.clicks for link in links)
    total_conversions = sum(link.conversions for link in links)
    overall_conversion_rate = round(total_conversions / total_clicks * 100, 2) if total_clicks > 0 else 0.0

    # Calculate today's stats
    clicks_today = 0
    conversions_today = 0

    for link in links:
        for event in link.click_events:
            if event.clicked_at >= day_ago:
                clicks_today += 1
                if event.converted:
                    conversions_today += 1

    # Get top campaigns by clicks
    campaign_stats: dict[uuid.UUID, dict] = {}
    for link in links:
        if link.campaign_id not in campaign_stats:
            campaign_stats[link.campaign_id] = {
                "campaign_id": str(link.campaign_id),
                "clicks": 0,
                "conversions": 0,
            }
        campaign_stats[link.campaign_id]["clicks"] += link.clicks
        campaign_stats[link.campaign_id]["conversions"] += link.conversions

    # Get campaign names
    if campaign_stats:
        campaign_result = await db.execute(
            select(Campaign).where(Campaign.id.in_(campaign_stats.keys()))
        )
        campaigns = {c.id: c.name for c in campaign_result.scalars().all()}
        for campaign_id, stats in campaign_stats.items():
            stats["name"] = campaigns.get(campaign_id, "Unknown")
            stats["conversion_rate"] = (
                round(stats["conversions"] / stats["clicks"] * 100, 2) if stats["clicks"] > 0 else 0.0
            )

    top_campaigns = sorted(campaign_stats.values(), key=lambda x: x["clicks"], reverse=True)[:5]

    return TrackingStatsResponse(
        total_links=total_links,
        total_clicks=total_clicks,
        total_conversions=total_conversions,
        overall_conversion_rate=overall_conversion_rate,
        clicks_today=clicks_today,
        conversions_today=conversions_today,
        top_campaigns=top_campaigns,
    )
