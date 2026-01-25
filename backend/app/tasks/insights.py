"""Background tasks for insights and intelligence generation."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.campaign import Campaign, GeneratedPost, TrackedLink
from app.models.feedback import FeedbackCategory, FeedbackItem, Sentiment
from app.models.insight import (
    DeepAnalysis,
    DeepAnalysisStatus,
    DeepAnalysisType,
    FeedbackTheme,
    Insight,
    InsightType,
    WeeklyReport,
)
from app.models.product import Product
from app.models.user import DEEP_ANALYSIS_CREDITS, Organization, SubscriptionTier
from app.services.ai.router import AIRouter

logger = logging.getLogger(__name__)
settings = get_settings()


def run_async(coro):
    """Run async function in sync context for Celery."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# =========================================================================
# Theme Clustering
# =========================================================================


@shared_task(bind=True, max_retries=3)
def cluster_feedback_themes(
    self, product_id: str, min_feedback_count: int = 10
) -> dict[str, Any]:
    """
    Cluster feedback into themes for a product.

    Args:
        product_id: The product to cluster feedback for
        min_feedback_count: Minimum feedback items required

    Returns:
        Summary of clustering results
    """
    return run_async(_cluster_feedback_themes(product_id, min_feedback_count))


async def _cluster_feedback_themes(
    product_id: str, min_feedback_count: int = 10
) -> dict[str, Any]:
    """Async implementation of feedback theme clustering."""
    async with async_session_factory() as db:
        # Get product
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()

        if not product:
            return {"error": "Product not found", "product_id": product_id}

        # Get recent feedback items (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        result = await db.execute(
            select(FeedbackItem)
            .where(
                FeedbackItem.product_id == product_id,
                FeedbackItem.created_at >= thirty_days_ago,
            )
            .order_by(FeedbackItem.created_at.desc())
            .limit(500)  # Cap for AI processing
        )
        feedback_items = result.scalars().all()

        if len(feedback_items) < min_feedback_count:
            return {
                "status": "skipped",
                "reason": f"Not enough feedback ({len(feedback_items)} < {min_feedback_count})",
                "product_id": product_id,
            }

        # Prepare feedback for AI
        feedback_data = [
            {
                "id": str(item.id),
                "text": item.text,
                "sentiment": item.sentiment,
                "category": item.category,
                "churn_risk": item.churn_risk,
            }
            for item in feedback_items
        ]

        # Run AI clustering
        ai_router = AIRouter(settings)
        try:
            cluster_result = await ai_router.cluster_themes(
                product_name=product.name,
                product_description=product.description,
                feedback_items=feedback_data,
            )
        except Exception as e:
            logger.error(f"AI clustering failed for {product_id}: {e}")
            return {"error": "AI clustering failed", "details": str(e)}

        # Deactivate old themes
        await db.execute(
            FeedbackTheme.__table__.update()
            .where(FeedbackTheme.product_id == product_id)
            .values(is_active=False)
        )

        # Create new themes
        themes_created = 0
        for theme_data in cluster_result.get("themes", []):
            # Map feedback indices to actual IDs
            feedback_indices = theme_data.get("feedback_indices", [])
            sample_ids = [
                feedback_data[i]["id"]
                for i in feedback_indices[:5]  # Store up to 5 sample IDs
                if i < len(feedback_data)
            ]

            theme = FeedbackTheme(
                product_id=product_id,
                name=theme_data.get("name", "Unnamed Theme"),
                description=theme_data.get("description", ""),
                feedback_count=len(feedback_indices),
                sentiment_breakdown=theme_data.get("sentiment_breakdown", {}),
                urgency=theme_data.get("urgency", "medium"),
                sample_feedback_ids=sample_ids,
                keywords=theme_data.get("keywords", []),
                is_active=True,
            )
            db.add(theme)
            themes_created += 1

        await db.commit()

        logger.info(
            f"Clustered {len(feedback_items)} feedback items into {themes_created} themes for {product.name}"
        )

        return {
            "status": "completed",
            "product_id": product_id,
            "themes_created": themes_created,
            "feedback_processed": len(feedback_items),
            "summary": cluster_result.get("summary", ""),
        }


# =========================================================================
# Weekly Reports
# =========================================================================


@shared_task(bind=True, max_retries=3)
def generate_weekly_report(self, product_id: str) -> dict[str, Any]:
    """
    Generate a weekly report for a product.

    Args:
        product_id: The product to generate report for

    Returns:
        Summary of report generation
    """
    return run_async(_generate_weekly_report(product_id))


async def _generate_weekly_report(product_id: str) -> dict[str, Any]:
    """Async implementation of weekly report generation."""
    async with async_session_factory() as db:
        # Get product with organization
        result = await db.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.organization))
        )
        product = result.scalar_one_or_none()

        if not product:
            return {"error": "Product not found", "product_id": product_id}

        # Calculate week boundaries (Monday to Sunday)
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday() + 7)  # Last Monday
        week_end = week_start + timedelta(days=6)  # Last Sunday
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(week_end, datetime.max.time())

        # Check if report already exists for this week
        existing = await db.execute(
            select(WeeklyReport).where(
                WeeklyReport.product_id == product_id,
                WeeklyReport.week_start == week_start_dt,
            )
        )
        if existing.scalar_one_or_none():
            return {
                "status": "skipped",
                "reason": "Report already exists for this week",
                "product_id": product_id,
            }

        # Gather marketing stats
        marketing_stats = await _gather_marketing_stats(db, product_id, week_start_dt, week_end_dt)

        # Gather feedback stats
        feedback_stats = await _gather_feedback_stats(db, product_id, week_start_dt, week_end_dt)

        # Generate AI report
        ai_router = AIRouter(settings)
        try:
            report_content = await ai_router.generate_weekly_report(
                product_name=product.name,
                start_date=week_start.isoformat(),
                end_date=week_end.isoformat(),
                marketing_stats=json.dumps(marketing_stats, indent=2),
                feedback_summary=json.dumps(feedback_stats, indent=2),
                mention_stats=json.dumps(feedback_stats.get("by_source", {}), indent=2),
            )
        except Exception as e:
            logger.error(f"AI report generation failed for {product_id}: {e}")
            report_content = {}

        # Create the report
        report = WeeklyReport(
            product_id=product_id,
            week_start=week_start_dt,
            week_end=week_end_dt,
            posts_published=marketing_stats.get("posts_published", 0),
            total_clicks=marketing_stats.get("total_clicks", 0),
            total_conversions=marketing_stats.get("total_conversions", 0),
            conversion_rate=marketing_stats.get("conversion_rate", 0.0),
            best_performing_post=marketing_stats.get("best_post"),
            new_mentions=feedback_stats.get("total_count", 0),
            sentiment_score=feedback_stats.get("sentiment_score", 0.0),
            sentiment_change=feedback_stats.get("sentiment_change", 0.0),
            top_complaints=report_content.get("sentiment", {}).get("top_complaints", []),
            top_praise=report_content.get("sentiment", {}).get("top_praise", []),
            executive_summary=report_content.get("executive_summary"),
            marketing_analysis=report_content.get("marketing_performance"),
            sentiment_analysis=report_content.get("sentiment"),
            recommended_actions=report_content.get("recommended_actions", []),
            next_week_focus=report_content.get("next_week_focus"),
        )
        db.add(report)

        # Generate insights from the report
        await _create_insights_from_report(db, product, report, report_content)

        await db.commit()

        logger.info(f"Generated weekly report for {product.name} ({week_start} to {week_end})")

        return {
            "status": "completed",
            "product_id": product_id,
            "report_id": str(report.id),
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
        }


async def _gather_marketing_stats(
    db, product_id: str, start: datetime, end: datetime
) -> dict[str, Any]:
    """Gather marketing statistics for the period."""
    # Count published posts
    posts_result = await db.execute(
        select(func.count(GeneratedPost.id))
        .join(Campaign)
        .where(
            Campaign.product_id == product_id,
            GeneratedPost.is_posted == True,
            GeneratedPost.created_at >= start,
            GeneratedPost.created_at <= end,
        )
    )
    posts_published = posts_result.scalar() or 0

    # Get link stats
    links_result = await db.execute(
        select(
            func.sum(TrackedLink.clicks).label("clicks"),
            func.sum(TrackedLink.conversions).label("conversions"),
        )
        .join(Campaign)
        .where(
            Campaign.product_id == product_id,
            TrackedLink.created_at >= start,
            TrackedLink.created_at <= end,
        )
    )
    link_stats = links_result.one()
    total_clicks = link_stats.clicks or 0
    total_conversions = link_stats.conversions or 0
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0

    # Best performing post (by clicks)
    best_post_result = await db.execute(
        select(GeneratedPost)
        .join(Campaign)
        .join(TrackedLink, Campaign.id == TrackedLink.campaign_id)
        .where(
            Campaign.product_id == product_id,
            GeneratedPost.is_posted == True,
        )
        .order_by(TrackedLink.clicks.desc())
        .limit(1)
    )
    best_post = best_post_result.scalar_one_or_none()

    return {
        "posts_published": posts_published,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "conversion_rate": round(conversion_rate, 2),
        "best_post": best_post.title if best_post else None,
    }


async def _gather_feedback_stats(
    db, product_id: str, start: datetime, end: datetime
) -> dict[str, Any]:
    """Gather feedback statistics for the period."""
    # Count feedback
    count_result = await db.execute(
        select(func.count(FeedbackItem.id)).where(
            FeedbackItem.product_id == product_id,
            FeedbackItem.created_at >= start,
            FeedbackItem.created_at <= end,
        )
    )
    total_count = count_result.scalar() or 0

    if total_count == 0:
        return {
            "total_count": 0,
            "sentiment_score": 0.0,
            "sentiment_change": 0.0,
            "by_sentiment": {},
            "by_source": {},
            "by_category": {},
        }

    # Sentiment breakdown
    sentiment_result = await db.execute(
        select(FeedbackItem.sentiment, func.count(FeedbackItem.id))
        .where(
            FeedbackItem.product_id == product_id,
            FeedbackItem.created_at >= start,
            FeedbackItem.created_at <= end,
        )
        .group_by(FeedbackItem.sentiment)
    )
    by_sentiment = {row[0]: row[1] for row in sentiment_result.all()}

    # Source breakdown
    source_result = await db.execute(
        select(FeedbackItem.source, func.count(FeedbackItem.id))
        .where(
            FeedbackItem.product_id == product_id,
            FeedbackItem.created_at >= start,
            FeedbackItem.created_at <= end,
        )
        .group_by(FeedbackItem.source)
    )
    by_source = {row[0]: row[1] for row in source_result.all()}

    # Category breakdown
    category_result = await db.execute(
        select(FeedbackItem.category, func.count(FeedbackItem.id))
        .where(
            FeedbackItem.product_id == product_id,
            FeedbackItem.created_at >= start,
            FeedbackItem.created_at <= end,
        )
        .group_by(FeedbackItem.category)
    )
    by_category = {row[0]: row[1] for row in category_result.all()}

    # Calculate sentiment score (-1 to 1)
    positive = by_sentiment.get("positive", 0)
    negative = by_sentiment.get("negative", 0)
    sentiment_score = (positive - negative) / total_count if total_count > 0 else 0.0

    # Get previous week's sentiment for comparison
    prev_start = start - timedelta(days=7)
    prev_end = end - timedelta(days=7)
    prev_result = await db.execute(
        select(FeedbackItem.sentiment, func.count(FeedbackItem.id))
        .where(
            FeedbackItem.product_id == product_id,
            FeedbackItem.created_at >= prev_start,
            FeedbackItem.created_at <= prev_end,
        )
        .group_by(FeedbackItem.sentiment)
    )
    prev_sentiment = {row[0]: row[1] for row in prev_result.all()}
    prev_total = sum(prev_sentiment.values())
    prev_positive = prev_sentiment.get("positive", 0)
    prev_negative = prev_sentiment.get("negative", 0)
    prev_score = (prev_positive - prev_negative) / prev_total if prev_total > 0 else 0.0
    sentiment_change = sentiment_score - prev_score

    return {
        "total_count": total_count,
        "sentiment_score": round(sentiment_score, 3),
        "sentiment_change": round(sentiment_change, 3),
        "by_sentiment": by_sentiment,
        "by_source": by_source,
        "by_category": by_category,
    }


async def _create_insights_from_report(
    db, product: Product, report: WeeklyReport, report_content: dict
):
    """Create insights from the weekly report."""
    insights_to_create = []

    # Create insights from recommended actions
    for action in report_content.get("recommended_actions", [])[:3]:
        insight = Insight(
            product_id=product.id,
            type=InsightType.ACTION_REQUIRED,
            title=action.get("action", "")[:500],
            description=action.get("reason", ""),
            priority=action.get("priority", "medium"),
            evidence=[f"From weekly report {report.week_start.date()} to {report.week_end.date()}"],
            suggested_action=action.get("action"),
            source="weekly_report",
            confidence=0.8,
        )
        insights_to_create.append(insight)

    # Check for sentiment shift
    if abs(report.sentiment_change) >= 0.15:
        direction = "improved" if report.sentiment_change > 0 else "declined"
        insight = Insight(
            product_id=product.id,
            type=InsightType.SENTIMENT_SHIFT,
            title=f"Sentiment {direction} by {abs(report.sentiment_change)*100:.1f}%",
            description=f"Customer sentiment has {direction} compared to last week.",
            priority="high" if report.sentiment_change < -0.15 else "medium",
            evidence=[
                f"Current sentiment score: {report.sentiment_score:.2f}",
                f"Change from last week: {report.sentiment_change:+.2f}",
            ],
            suggested_action=f"Review recent {'negative' if report.sentiment_change < 0 else 'positive'} feedback to understand the shift.",
            source="weekly_report",
            confidence=0.9,
        )
        insights_to_create.append(insight)

    # Add all insights
    for insight in insights_to_create:
        db.add(insight)


@shared_task
def generate_all_weekly_reports() -> dict[str, Any]:
    """
    Generate weekly reports for all active products.
    Called by Celery beat every Monday.
    """
    return run_async(_generate_all_weekly_reports())


async def _generate_all_weekly_reports() -> dict[str, Any]:
    """Async implementation of generating all weekly reports."""
    async with async_session_factory() as db:
        # Get all products
        result = await db.execute(select(Product.id))
        product_ids = [str(row[0]) for row in result.all()]

    # Queue individual report tasks
    for product_id in product_ids:
        try:
            generate_weekly_report.delay(product_id)
        except Exception as e:
            logger.warning(f"Could not queue weekly report for {product_id}: {e}")

    return {
        "status": "queued",
        "products_count": len(product_ids),
    }


# =========================================================================
# Deep Analysis (Pro+ Feature)
# =========================================================================


@shared_task(bind=True, max_retries=2)
def run_deep_analysis(self, analysis_id: str) -> dict[str, Any]:
    """
    Run a deep analysis.

    Args:
        analysis_id: The deep analysis record ID

    Returns:
        Analysis results summary
    """
    return run_async(_run_deep_analysis(analysis_id))


async def _run_deep_analysis(analysis_id: str) -> dict[str, Any]:
    """Async implementation of deep analysis."""
    async with async_session_factory() as db:
        # Get analysis record
        result = await db.execute(
            select(DeepAnalysis)
            .where(DeepAnalysis.id == analysis_id)
            .options(selectinload(DeepAnalysis.product))
        )
        analysis = result.scalar_one_or_none()

        if not analysis:
            return {"error": "Analysis not found", "analysis_id": analysis_id}

        # Mark as processing
        analysis.status = DeepAnalysisStatus.PROCESSING
        analysis.started_at = datetime.utcnow()
        await db.commit()

        product = analysis.product
        ai_router = AIRouter(settings)

        try:
            if analysis.analysis_type == DeepAnalysisType.CHURN_ANALYSIS:
                results = await _run_churn_analysis(db, product, ai_router)
            elif analysis.analysis_type == DeepAnalysisType.COMPETITOR_INTELLIGENCE:
                results = await _run_competitor_analysis(db, product, ai_router)
            elif analysis.analysis_type == DeepAnalysisType.CONTENT_STRATEGY:
                results = await _run_content_analysis(db, product, ai_router)
            else:
                raise ValueError(f"Unknown analysis type: {analysis.analysis_type}")

            # Update analysis with results
            analysis.status = DeepAnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            analysis.results = results
            analysis.summary = results.get("summary", "")
            analysis.recommendations = results.get("recommendations", [])
            analysis.data_points_analyzed = results.get("data_points", 0)

            # Generate insights from the analysis
            await _create_insights_from_deep_analysis(db, product, analysis, results)

            await db.commit()

            logger.info(f"Completed deep analysis {analysis_id} for {product.name}")

            return {
                "status": "completed",
                "analysis_id": str(analysis.id),
                "analysis_type": analysis.analysis_type.value,
                "summary": analysis.summary,
            }

        except Exception as e:
            logger.error(f"Deep analysis {analysis_id} failed: {e}")
            analysis.status = DeepAnalysisStatus.FAILED
            analysis.error_message = str(e)
            await db.commit()

            return {
                "status": "failed",
                "analysis_id": str(analysis.id),
                "error": str(e),
            }


async def _run_churn_analysis(db, product: Product, ai_router: AIRouter) -> dict:
    """Run churn-focused deep analysis."""
    # Gather high-risk feedback
    high_risk_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.churn_risk >= 0.5,
        )
        .order_by(FeedbackItem.churn_risk.desc())
        .limit(50)
    )
    high_risk = high_risk_result.scalars().all()

    # Gather negative feedback
    negative_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.sentiment == Sentiment.NEGATIVE.value,
        )
        .order_by(FeedbackItem.created_at.desc())
        .limit(100)
    )
    negative = negative_result.scalars().all()

    # Gather competitor mentions
    competitor_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.category == FeedbackCategory.COMPETITOR_MENTION.value,
        )
        .limit(50)
    )
    competitor_mentions = competitor_result.scalars().all()

    # Format for AI
    high_risk_text = "\n".join(
        f"- ({item.churn_risk:.2f}) {item.text[:300]}" for item in high_risk
    )
    negative_text = "\n".join(f"- {item.text[:300]}" for item in negative[:50])
    competitor_text = "\n".join(f"- {item.text[:300]}" for item in competitor_mentions)

    results = await ai_router.deep_analysis_churn(
        product_name=product.name,
        product_description=product.description,
        high_risk_feedback=high_risk_text or "No high-risk feedback found",
        negative_feedback=negative_text or "No negative feedback found",
        competitor_mentions=competitor_text or "No competitor mentions found",
    )

    results["data_points"] = len(high_risk) + len(negative) + len(competitor_mentions)
    return results


async def _run_competitor_analysis(db, product: Product, ai_router: AIRouter) -> dict:
    """Run competitor-focused deep analysis."""
    # Gather competitor-related feedback
    competitor_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.category == FeedbackCategory.COMPETITOR_MENTION.value,
        )
        .limit(100)
    )
    competitor_feedback = competitor_result.scalars().all()

    # Gather feature requests
    feature_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.category == FeedbackCategory.FEATURE_REQUEST.value,
        )
        .limit(100)
    )
    feature_requests = feature_result.scalars().all()

    # Format for AI
    competitor_text = "\n".join(f"- {item.text[:400]}" for item in competitor_feedback)
    feature_text = "\n".join(f"- {item.text[:400]}" for item in feature_requests[:50])

    results = await ai_router.deep_analysis_competitor(
        product_name=product.name,
        product_description=product.description,
        competitor_feedback=competitor_text or "No competitor feedback found",
        comparison_requests="",  # Could be extracted from questions
        competitor_feature_requests=feature_text or "No feature requests found",
    )

    results["data_points"] = len(competitor_feedback) + len(feature_requests)
    return results


async def _run_content_analysis(db, product: Product, ai_router: AIRouter) -> dict:
    """Run content strategy deep analysis."""
    from app.models.audience import AudienceSource

    # Gather audience sources
    sources_result = await db.execute(
        select(AudienceSource)
        .where(AudienceSource.product_id == product.id)
        .order_by(AudienceSource.relevance_score.desc())
        .limit(20)
    )
    sources = sources_result.scalars().all()

    # Gather questions
    questions_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.category == FeedbackCategory.QUESTION.value,
        )
        .limit(50)
    )
    questions = questions_result.scalars().all()

    # Gather complaints (pain points)
    complaints_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.category == FeedbackCategory.COMPLAINT.value,
        )
        .limit(50)
    )
    complaints = complaints_result.scalars().all()

    # Gather praise
    praise_result = await db.execute(
        select(FeedbackItem)
        .where(
            FeedbackItem.product_id == product.id,
            FeedbackItem.category == FeedbackCategory.PRAISE.value,
        )
        .limit(50)
    )
    praise = praise_result.scalars().all()

    # Get top performing posts
    posts_result = await db.execute(
        select(GeneratedPost)
        .join(Campaign)
        .where(
            Campaign.product_id == product.id,
            GeneratedPost.is_posted == True,
        )
        .limit(20)
    )
    posts = posts_result.scalars().all()

    # Format for AI
    sources_text = "\n".join(
        f"- {s.name} ({s.platform}, relevance: {s.relevance_score:.2f})"
        for s in sources
    )
    questions_text = "\n".join(f"- {item.text[:300]}" for item in questions)
    pain_text = "\n".join(f"- {item.text[:300]}" for item in complaints)
    praise_text = "\n".join(f"- {item.text[:300]}" for item in praise)
    posts_text = "\n".join(
        f"- [{p.style}] {p.title or 'No title'}" for p in posts
    )

    results = await ai_router.deep_analysis_content(
        product_name=product.name,
        product_description=product.description,
        audience_sources=sources_text or "No audience sources found",
        top_content=posts_text or "No posted content found",
        user_questions=questions_text or "No questions found",
        pain_points=pain_text or "No complaints found",
        praise_feedback=praise_text or "No praise found",
    )

    results["data_points"] = (
        len(sources) + len(questions) + len(complaints) + len(praise) + len(posts)
    )
    return results


async def _create_insights_from_deep_analysis(
    db, product: Product, analysis: DeepAnalysis, results: dict
):
    """Create insights from deep analysis results."""
    ai_router = AIRouter(settings)

    try:
        insight_result = await ai_router.generate_insights(
            product_name=product.name,
            analysis_type=analysis.analysis_type.value,
            analysis_results=json.dumps(results, indent=2)[:8000],  # Cap length
        )

        for insight_data in insight_result.get("insights", [])[:5]:
            insight = Insight(
                product_id=product.id,
                type=insight_data.get("type", InsightType.ACTION_REQUIRED.value),
                title=insight_data.get("title", "")[:500],
                description=insight_data.get("description", ""),
                priority=insight_data.get("priority", "medium"),
                evidence=insight_data.get("evidence", []),
                suggested_action=insight_data.get("suggested_action"),
                confidence=min(1.0, max(0.0, insight_data.get("confidence", 0.8))),
                source=f"deep_analysis_{analysis.analysis_type.value}",
            )
            db.add(insight)

    except Exception as e:
        logger.warning(f"Failed to generate insights from deep analysis: {e}")


# =========================================================================
# Credit Management
# =========================================================================


@shared_task
def reset_monthly_credits() -> dict[str, Any]:
    """
    Reset deep analysis credits for all organizations.
    Called by Celery beat on the 1st of each month.
    """
    return run_async(_reset_monthly_credits())


async def _reset_monthly_credits() -> dict[str, Any]:
    """Async implementation of credit reset."""
    async with async_session_factory() as db:
        # Reset credits based on tier
        for tier, credits in DEEP_ANALYSIS_CREDITS.items():
            if credits >= 0:  # Don't update unlimited (-1)
                await db.execute(
                    Organization.__table__.update()
                    .where(Organization.subscription_tier == tier.value)
                    .values(
                        deep_analysis_credits=credits,
                        credits_reset_at=datetime.utcnow(),
                    )
                )

        await db.commit()

    logger.info("Reset monthly deep analysis credits for all organizations")
    return {"status": "completed"}
