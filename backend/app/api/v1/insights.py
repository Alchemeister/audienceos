"""Insights API endpoints for Phase 4: Insights & Intelligence."""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import AIRouterDep, AsyncSessionDep, CurrentUserDep
from app.core.exceptions import TierLimitError
from app.models.insight import (
    DeepAnalysis,
    DeepAnalysisStatus,
    DeepAnalysisType,
    FeedbackTheme,
    Insight,
    WeeklyReport,
)
from app.models.product import Product
from app.models.user import DEEP_ANALYSIS_CREDITS, Organization, SubscriptionTier
from app.schemas.insight import (
    CreditsResponse,
    DeepAnalysisListResponse,
    DeepAnalysisRequest,
    DeepAnalysisResponse,
    FeedbackThemeResponse,
    InsightActionRequest,
    InsightListResponse,
    InsightResponse,
    ThemeClusterRequest,
    ThemeClusterResponse,
    ThemeListResponse,
    WeeklyReportListResponse,
    WeeklyReportResponse,
    WeeklyReportSummary,
)
from app.tasks.insights import cluster_feedback_themes, generate_weekly_report, run_deep_analysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])


# =========================================================================
# Theme Clustering Endpoints
# =========================================================================


@router.post(
    "/cluster",
    response_model=ThemeClusterResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_theme_clustering(
    product_id: uuid.UUID,
    data: ThemeClusterRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """
    Trigger theme clustering for a product's feedback.

    This is an async operation - returns immediately with a task ID.
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
        raise HTTPException(status_code=404, detail="Product not found")

    # Queue the clustering task
    try:
        task = cluster_feedback_themes.delay(
            str(product_id),
            min_feedback_count=data.min_feedback_count,
        )
        return ThemeClusterResponse(
            task_id=task.id,
            status="queued",
            message="Theme clustering started. Check /insights/themes for results.",
        )
    except Exception as e:
        logger.error(f"Failed to queue clustering task: {e}")
        raise HTTPException(
            status_code=503,
            detail="Could not start clustering task. Please try again.",
        )


@router.get("/themes", response_model=ThemeListResponse)
async def list_themes(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    active_only: bool = Query(True, description="Only return active themes"),
):
    """
    List feedback themes for a product.

    Returns clustered themes with sentiment breakdown and sample feedback.
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
        raise HTTPException(status_code=404, detail="Product not found")

    # Get themes
    query = select(FeedbackTheme).where(FeedbackTheme.product_id == product_id)
    if active_only:
        query = query.where(FeedbackTheme.is_active == True)
    query = query.order_by(FeedbackTheme.feedback_count.desc())

    result = await db.execute(query)
    themes = result.scalars().all()

    # Get last clustering time
    last_clustered = None
    if themes:
        last_clustered = max(t.created_at for t in themes)

    return ThemeListResponse(
        themes=[FeedbackThemeResponse.model_validate(t) for t in themes],
        total=len(themes),
        last_clustered_at=last_clustered,
    )


@router.get("/themes/{theme_id}", response_model=FeedbackThemeResponse)
async def get_theme(
    theme_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """Get a specific feedback theme."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(FeedbackTheme)
        .join(Product)
        .where(
            FeedbackTheme.id == theme_id,
            Product.organization_id == org_id,
        )
    )
    theme = result.scalar_one_or_none()

    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    return FeedbackThemeResponse.model_validate(theme)


# =========================================================================
# Weekly Report Endpoints
# =========================================================================


@router.get("/reports", response_model=WeeklyReportListResponse)
async def list_reports(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    limit: int = Query(10, ge=1, le=52),
    offset: int = Query(0, ge=0),
):
    """
    List weekly reports for a product.

    Returns a paginated list of report summaries.
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
        raise HTTPException(status_code=404, detail="Product not found")

    # Count total
    count_result = await db.execute(
        select(func.count(WeeklyReport.id)).where(
            WeeklyReport.product_id == product_id
        )
    )
    total = count_result.scalar() or 0

    # Get reports
    result = await db.execute(
        select(WeeklyReport)
        .where(WeeklyReport.product_id == product_id)
        .order_by(WeeklyReport.week_start.desc())
        .limit(limit)
        .offset(offset)
    )
    reports = result.scalars().all()

    return WeeklyReportListResponse(
        reports=[
            WeeklyReportSummary(
                id=r.id,
                product_id=r.product_id,
                week_start=r.week_start,
                week_end=r.week_end,
                new_mentions=r.new_mentions,
                sentiment_score=r.sentiment_score,
                sentiment_change=r.sentiment_change,
                email_sent=r.email_sent,
                created_at=r.created_at,
            )
            for r in reports
        ],
        total=total,
    )


@router.get("/reports/{report_id}", response_model=WeeklyReportResponse)
async def get_report(
    report_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """Get a full weekly report with all details."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(WeeklyReport)
        .join(Product)
        .where(
            WeeklyReport.id == report_id,
            Product.organization_id == org_id,
        )
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return WeeklyReportResponse.model_validate(report)


@router.post(
    "/reports/generate",
    response_model=ThemeClusterResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_report_generation(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """
    Manually trigger weekly report generation.

    Useful for testing or generating on-demand reports.
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
        raise HTTPException(status_code=404, detail="Product not found")

    # Queue the report generation task
    try:
        task = generate_weekly_report.delay(str(product_id))
        return ThemeClusterResponse(
            task_id=task.id,
            status="queued",
            message="Report generation started. Check /insights/reports for results.",
        )
    except Exception as e:
        logger.error(f"Failed to queue report task: {e}")
        raise HTTPException(
            status_code=503,
            detail="Could not start report generation. Please try again.",
        )


# =========================================================================
# Insights Endpoints
# =========================================================================


@router.get("", response_model=InsightListResponse)
async def list_insights(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_dismissed: bool = Query(False),
    include_actioned: bool = Query(True),
):
    """
    List AI-generated insights for a product.

    Insights are recommendations based on weekly reports and deep analysis.
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
        raise HTTPException(status_code=404, detail="Product not found")

    # Build query
    query = select(Insight).where(Insight.product_id == product_id)

    if not include_dismissed:
        query = query.where(Insight.is_dismissed == False)
    if not include_actioned:
        query = query.where(Insight.is_actioned == False)

    # Count total
    count_query = select(func.count(Insight.id)).where(Insight.product_id == product_id)
    if not include_dismissed:
        count_query = count_query.where(Insight.is_dismissed == False)
    if not include_actioned:
        count_query = count_query.where(Insight.is_actioned == False)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Get insights
    result = await db.execute(
        query.order_by(Insight.created_at.desc()).limit(limit).offset(offset)
    )
    insights = result.scalars().all()

    return InsightListResponse(
        insights=[InsightResponse.model_validate(i) for i in insights],
        total=total,
    )


@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """Get a specific insight."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(Insight)
        .join(Product)
        .where(
            Insight.id == insight_id,
            Product.organization_id == org_id,
        )
    )
    insight = result.scalar_one_or_none()

    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    return InsightResponse.model_validate(insight)


@router.patch("/{insight_id}", response_model=InsightResponse)
async def update_insight(
    insight_id: uuid.UUID,
    data: InsightActionRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """Mark an insight as actioned or dismissed."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(Insight)
        .join(Product)
        .where(
            Insight.id == insight_id,
            Product.organization_id == org_id,
        )
    )
    insight = result.scalar_one_or_none()

    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    if data.is_actioned:
        insight.is_actioned = True
        insight.actioned_at = datetime.utcnow()

    if data.is_dismissed:
        insight.is_dismissed = True

    await db.commit()
    await db.refresh(insight)

    return InsightResponse.model_validate(insight)


# =========================================================================
# Deep Analysis Endpoints (Pro+ Feature)
# =========================================================================


@router.get("/credits", response_model=CreditsResponse)
async def get_credits(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """Get available deep analysis credits for the organization."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    tier_credits = DEEP_ANALYSIS_CREDITS.get(org.subscription_tier, 0)
    is_unlimited = tier_credits < 0

    return CreditsResponse(
        tier=org.subscription_tier.value,
        credits_remaining=org.deep_analysis_credits if not is_unlimited else -1,
        credits_total=tier_credits if tier_credits >= 0 else -1,
        is_unlimited=is_unlimited,
        reset_at=org.credits_reset_at,
    )


@router.post(
    "/analyze",
    response_model=DeepAnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_deep_analysis(
    product_id: uuid.UUID,
    data: DeepAnalysisRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """
    Trigger a deep analysis (Pro+ feature).

    Types available:
    - churn_analysis: Analyze churn signals and risk
    - competitor_intelligence: Analyze competitor mentions
    - content_strategy: Generate content strategy recommendations

    Uses credits: Pro gets 4/month, Agency unlimited.
    """
    org_id = uuid.UUID(current_user["organization_id"])

    # Verify product ownership
    result = await db.execute(
        select(Product)
        .where(
            Product.id == product_id,
            Product.organization_id == org_id,
        )
        .options(selectinload(Product.organization))
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    org = product.organization

    # Check tier - Indie cannot use deep analysis
    if org.subscription_tier == SubscriptionTier.INDIE:
        raise TierLimitError(
            "Deep analysis is a Pro+ feature",
            details={"required_tier": "pro", "current_tier": "indie"},
        )

    # Check credits (Agency has unlimited = -1)
    tier_credits = DEEP_ANALYSIS_CREDITS.get(org.subscription_tier, 0)
    if tier_credits >= 0 and org.deep_analysis_credits <= 0:
        raise TierLimitError(
            "No deep analysis credits remaining",
            details={
                "credits_remaining": 0,
                "reset_at": org.credits_reset_at.isoformat() if org.credits_reset_at else None,
            },
        )

    # Create analysis record
    analysis = DeepAnalysis(
        product_id=product_id,
        organization_id=org_id,
        analysis_type=data.analysis_type,
        status=DeepAnalysisStatus.PENDING,
    )
    db.add(analysis)

    # Deduct credit (if not unlimited)
    if tier_credits >= 0:
        org.deep_analysis_credits -= 1

    await db.commit()
    await db.refresh(analysis)

    # Queue the analysis task
    try:
        run_deep_analysis.delay(str(analysis.id))
    except Exception as e:
        logger.error(f"Failed to queue deep analysis task: {e}")
        # Don't fail - the analysis record exists and can be retried

    return DeepAnalysisResponse.model_validate(analysis)


@router.get("/analyze", response_model=DeepAnalysisListResponse)
async def list_deep_analyses(
    product_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    """List deep analyses for a product."""
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
        raise HTTPException(status_code=404, detail="Product not found")

    # Count total
    count_result = await db.execute(
        select(func.count(DeepAnalysis.id)).where(
            DeepAnalysis.product_id == product_id
        )
    )
    total = count_result.scalar() or 0

    # Get analyses
    result = await db.execute(
        select(DeepAnalysis)
        .where(DeepAnalysis.product_id == product_id)
        .order_by(DeepAnalysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    analyses = result.scalars().all()

    return DeepAnalysisListResponse(
        analyses=[DeepAnalysisResponse.model_validate(a) for a in analyses],
        total=total,
    )


@router.get("/analyze/{analysis_id}", response_model=DeepAnalysisResponse)
async def get_deep_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """Get a specific deep analysis with results."""
    org_id = uuid.UUID(current_user["organization_id"])

    result = await db.execute(
        select(DeepAnalysis).where(
            DeepAnalysis.id == analysis_id,
            DeepAnalysis.organization_id == org_id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return DeepAnalysisResponse.model_validate(analysis)
