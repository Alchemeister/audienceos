"""Feedback endpoints with filtering, stats, import, and webhooks."""

import csv
import hashlib
import hmac
import io
import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, File, Header, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select

from app.api.deps import AIRouterDep, AsyncSessionDep, CurrentUserDep, SettingsDep
from app.models.feedback import FeedbackCategory, FeedbackItem, Sentiment, Urgency
from app.models.product import Product
from app.schemas.common import Platform
from app.schemas.feedback import (
    FeedbackAnalyzeRequest,
    FeedbackAnalyzeResponse,
    FeedbackImportResponse,
    FeedbackItemResponse,
    FeedbackListResponse,
    FeedbackStatsResponse,
    FeedbackWebhookPayload,
    SentimentTrend,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/analyze", response_model=FeedbackAnalyzeResponse)
async def analyze_feedback(
    data: FeedbackAnalyzeRequest,
    ai_router: AIRouterDep,
    current_user: CurrentUserDep,
) -> FeedbackAnalyzeResponse:
    """
    Analyze a piece of feedback text using AI.

    Uses the EXPENSIVE tier model for nuanced sentiment analysis.
    Does not store the feedback - use this for one-off analysis.
    """
    result = await ai_router.analyze_sentiment(
        text=data.text,
        product_description=data.context.get("product_description", "A software product"),
    )

    return FeedbackAnalyzeResponse(
        sentiment=result.get("sentiment", "neutral"),
        emotion=result.get("emotion"),
        category=result.get("category", "question"),
        subcategory=result.get("subcategory"),
        urgency=result.get("urgency", "medium"),
        product_area=result.get("product_area"),
        key_phrases=result.get("key_phrases", []),
        churn_risk=result.get("churn_risk", 0.0),
        suggested_action=result.get("suggested_action"),
    )


@router.get("", response_model=FeedbackListResponse)
async def list_feedback(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    # Filters
    source: Platform | None = None,
    sentiment: str | None = None,
    category: str | None = None,
    urgency: str | None = None,
    is_actioned: bool | None = None,
    # Date range
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    # Search
    search: str | None = Query(None, min_length=2, max_length=200),
    # Pagination
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    # Sorting
    sort_by: str = Query("created_at", regex="^(created_at|sentiment|urgency|churn_risk)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
) -> FeedbackListResponse:
    """
    List feedback items for a product with comprehensive filters.

    Filters:
    - source: Filter by platform (reddit, twitter, hackernews, etc.)
    - sentiment: Filter by sentiment (positive, negative, neutral, mixed)
    - category: Filter by category (bug, feature_request, praise, etc.)
    - urgency: Filter by urgency (low, medium, high, critical)
    - is_actioned: Filter by actioned status
    - start_date/end_date: Filter by date range
    - search: Full-text search in feedback text

    Sorting:
    - sort_by: Field to sort by (created_at, sentiment, urgency, churn_risk)
    - sort_order: asc or desc
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

    # Build base query
    query = select(FeedbackItem).where(FeedbackItem.product_id == product_id)

    # Apply filters
    if source:
        query = query.where(FeedbackItem.source == source.value)
    if sentiment:
        query = query.where(FeedbackItem.sentiment == sentiment)
    if category:
        query = query.where(FeedbackItem.category == category)
    if urgency:
        query = query.where(FeedbackItem.urgency == urgency)
    if is_actioned is not None:
        query = query.where(FeedbackItem.is_actioned == is_actioned)

    # Date range
    if start_date:
        query = query.where(FeedbackItem.created_at >= start_date)
    if end_date:
        query = query.where(FeedbackItem.created_at <= end_date)

    # Text search (basic LIKE for SQLite/PostgreSQL compatibility)
    if search:
        query = query.where(FeedbackItem.text.ilike(f"%{search}%"))

    # Sorting
    sort_column = getattr(FeedbackItem, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Get paginated items
    result = await db.execute(query.limit(limit).offset(offset))
    items = result.scalars().all()

    # Get total count with same filters
    count_query = select(func.count(FeedbackItem.id)).where(FeedbackItem.product_id == product_id)
    if source:
        count_query = count_query.where(FeedbackItem.source == source.value)
    if sentiment:
        count_query = count_query.where(FeedbackItem.sentiment == sentiment)
    if category:
        count_query = count_query.where(FeedbackItem.category == category)
    if urgency:
        count_query = count_query.where(FeedbackItem.urgency == urgency)
    if is_actioned is not None:
        count_query = count_query.where(FeedbackItem.is_actioned == is_actioned)
    if start_date:
        count_query = count_query.where(FeedbackItem.created_at >= start_date)
    if end_date:
        count_query = count_query.where(FeedbackItem.created_at <= end_date)
    if search:
        count_query = count_query.where(FeedbackItem.text.ilike(f"%{search}%"))

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return FeedbackListResponse(
        items=[FeedbackItemResponse.model_validate(item) for item in items],
        total=total,
    )


@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    days: int = Query(30, ge=1, le=365),
) -> FeedbackStatsResponse:
    """
    Get aggregated feedback statistics for a product.

    Includes:
    - Total counts by sentiment, category, source
    - Trends over time
    - Top keywords/phrases
    - Churn risk distribution
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

    # Date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Base query for period
    base = select(FeedbackItem).where(
        FeedbackItem.product_id == product_id,
        FeedbackItem.created_at >= start_date,
    )

    # Get all feedback in period
    result = await db.execute(base)
    items = result.scalars().all()

    # Total counts
    total_count = len(items)

    # Count by sentiment
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}
    for item in items:
        sent = item.sentiment if isinstance(item.sentiment, str) else item.sentiment.value
        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1

    # Count by category
    category_counts: dict[str, int] = {}
    for item in items:
        cat = item.category if isinstance(item.category, str) else item.category.value
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count by source
    source_counts: dict[str, int] = {}
    for item in items:
        src = item.source if isinstance(item.source, str) else item.source.value
        source_counts[src] = source_counts.get(src, 0) + 1

    # Count by urgency
    urgency_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for item in items:
        urg = item.urgency if isinstance(item.urgency, str) else item.urgency.value
        urgency_counts[urg] = urgency_counts.get(urg, 0) + 1

    # Calculate average churn risk
    churn_risks = [item.churn_risk for item in items if item.churn_risk is not None]
    avg_churn_risk = sum(churn_risks) / len(churn_risks) if churn_risks else 0.0

    # High churn risk count (> 0.7)
    high_churn_count = sum(1 for r in churn_risks if r > 0.7)

    # Aggregate key phrases
    phrase_counts: dict[str, int] = {}
    for item in items:
        for phrase in (item.key_phrases or []):
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

    # Top 20 phrases
    top_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    # Calculate sentiment trend (weekly buckets)
    sentiment_trend = []
    week_start = start_date
    while week_start < end_date:
        week_end = week_start + timedelta(days=7)
        week_items = [
            item for item in items
            if week_start <= item.created_at < week_end
        ]

        if week_items:
            week_positive = sum(1 for i in week_items if (i.sentiment if isinstance(i.sentiment, str) else i.sentiment.value) == "positive")
            week_negative = sum(1 for i in week_items if (i.sentiment if isinstance(i.sentiment, str) else i.sentiment.value) == "negative")
            week_total = len(week_items)

            # Sentiment score: (positive - negative) / total, ranges from -1 to 1
            score = (week_positive - week_negative) / week_total if week_total > 0 else 0

            sentiment_trend.append(SentimentTrend(
                date=week_start.date().isoformat(),
                score=round(score, 2),
                count=week_total,
            ))

        week_start = week_end

    # Actioned rate
    actioned_count = sum(1 for item in items if item.is_actioned)
    actioned_rate = actioned_count / total_count if total_count > 0 else 0.0

    return FeedbackStatsResponse(
        product_id=product_id,
        period_days=days,
        total_count=total_count,
        sentiment_counts=sentiment_counts,
        category_counts=category_counts,
        source_counts=source_counts,
        urgency_counts=urgency_counts,
        avg_churn_risk=round(avg_churn_risk, 3),
        high_churn_count=high_churn_count,
        top_phrases=[{"phrase": p, "count": c} for p, c in top_phrases],
        sentiment_trend=sentiment_trend,
        actioned_count=actioned_count,
        actioned_rate=round(actioned_rate, 3),
    )


@router.get("/{feedback_id}", response_model=FeedbackItemResponse)
async def get_feedback(
    feedback_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> FeedbackItemResponse:
    """Get a specific feedback item."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(FeedbackItem)
        .join(Product)
        .where(
            FeedbackItem.id == feedback_id,
            Product.organization_id == org_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    return FeedbackItemResponse.model_validate(item)


@router.post("/{feedback_id}/action", response_model=FeedbackItemResponse)
async def mark_feedback_actioned(
    feedback_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> FeedbackItemResponse:
    """Mark a feedback item as actioned."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(FeedbackItem)
        .join(Product)
        .where(
            FeedbackItem.id == feedback_id,
            Product.organization_id == org_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    item.is_actioned = True
    item.actioned_at = datetime.utcnow()
    await db.commit()
    await db.refresh(item)

    return FeedbackItemResponse.model_validate(item)


@router.post("/import", response_model=FeedbackImportResponse)
async def import_feedback_csv(
    product_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSessionDep = None,
    current_user: CurrentUserDep = None,
    ai_router: AIRouterDep = None,
) -> FeedbackImportResponse:
    """
    Import feedback from a CSV file.

    CSV format (with headers):
    - text (required): The feedback text
    - source (optional): Platform source (defaults to "manual")
    - author (optional): Author name/identifier
    - source_url (optional): Link to original
    - created_at (optional): Original timestamp (ISO format)

    Each row will be analyzed using the AI pipeline.
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

    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )

    # Read and parse CSV
    content = await file.read()
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        text_content = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text_content))

    imported = 0
    failed = 0
    errors = []
    product_context = f"{product.name}: {product.description}"

    for i, row in enumerate(reader):
        try:
            text = row.get("text", "").strip()
            if not text:
                errors.append(f"Row {i+1}: Missing text")
                failed += 1
                continue

            # Analyze with AI
            try:
                analysis = await ai_router.analyze_sentiment(
                    text=text,
                    product_description=product_context,
                )
            except Exception:
                # Use defaults on AI failure
                analysis = {
                    "sentiment": "neutral",
                    "category": "question",
                    "urgency": "medium",
                    "key_phrases": [],
                    "churn_risk": 0.0,
                }

            # Parse source
            source_str = row.get("source", "manual").lower().strip()
            valid_sources = ["reddit", "twitter", "hackernews", "github", "email", "widget", "manual"]
            source = source_str if source_str in valid_sources else "manual"

            # Parse date
            created_at_str = row.get("created_at", "")
            try:
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
            except ValueError:
                created_at = datetime.utcnow()

            # Create feedback item
            feedback_item = FeedbackItem(
                product_id=product_id,
                source=source,
                source_url=row.get("source_url", "")[:500] or None,
                author=row.get("author", "")[:255] or None,
                text=text[:10000],
                sentiment=analysis.get("sentiment", "neutral"),
                emotion=analysis.get("emotion"),
                category=analysis.get("category", "question"),
                subcategory=analysis.get("subcategory"),
                urgency=analysis.get("urgency", "medium"),
                product_area=analysis.get("product_area"),
                key_phrases=analysis.get("key_phrases", []),
                churn_risk=min(1.0, max(0.0, analysis.get("churn_risk", 0.0))),
                suggested_action=analysis.get("suggested_action"),
                raw_data={"import_row": i + 1},
                collected_at=created_at,
            )
            db.add(feedback_item)
            imported += 1

        except Exception as e:
            errors.append(f"Row {i+1}: {str(e)}")
            failed += 1

    await db.commit()

    return FeedbackImportResponse(
        imported=imported,
        failed=failed,
        errors=errors[:10] if errors else [],  # Limit error messages
    )


@router.post("/webhook", status_code=status.HTTP_201_CREATED)
async def receive_webhook(
    payload: FeedbackWebhookPayload,
    db: AsyncSessionDep,
    settings: SettingsDep,
    x_webhook_signature: str | None = Header(None),
) -> dict[str, Any]:
    """
    Receive feedback from external sources via webhook.

    Supports integrations with:
    - Support tools (Zendesk, Intercom, etc.)
    - Email parsers
    - Custom integrations

    Webhook signature verification:
    - Set WEBHOOK_SECRET in env
    - Send X-Webhook-Signature header with HMAC-SHA256 of body
    """
    # Verify webhook signature if secret is configured
    if settings.SECRET_KEY and settings.SECRET_KEY != "change-me-in-production":
        if not x_webhook_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Webhook signature required",
            )

        # Verify HMAC signature
        expected = hmac.new(
            settings.SECRET_KEY.encode(),
            payload.model_dump_json().encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(x_webhook_signature, expected):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

    # Verify product exists (no org check - webhook is authenticated by signature)
    result = await db.execute(
        select(Product).where(Product.id == payload.product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Use provided analysis or defaults
    analysis = payload.analysis or {}

    # Create feedback item
    feedback_item = FeedbackItem(
        product_id=payload.product_id,
        source=payload.source,
        source_url=payload.source_url,
        author=payload.author,
        author_id=payload.author_id,
        text=payload.text[:10000],
        sentiment=analysis.get("sentiment", "neutral"),
        emotion=analysis.get("emotion"),
        category=analysis.get("category", "question"),
        subcategory=analysis.get("subcategory"),
        urgency=analysis.get("urgency", "medium"),
        product_area=analysis.get("product_area"),
        key_phrases=analysis.get("key_phrases", []),
        churn_risk=min(1.0, max(0.0, analysis.get("churn_risk", 0.0))),
        suggested_action=analysis.get("suggested_action"),
        raw_data=payload.metadata or {},
        collected_at=datetime.utcnow(),
    )
    db.add(feedback_item)
    await db.commit()
    await db.refresh(feedback_item)

    return {
        "id": str(feedback_item.id),
        "status": "created",
    }
