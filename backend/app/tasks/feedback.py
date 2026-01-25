"""Background tasks for feedback collection and historical backfill."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.product import Product
from app.models.user import Organization, SubscriptionTier
from app.tasks.monitoring import (
    _filter_and_analyze_mentions,
    _store_feedback_items,
)
from app.services.ai.router import AIRouter
from app.services.research.reddit import RedditClient
from app.services.research.hackernews import HackerNewsClient

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


# Backfill days by subscription tier
BACKFILL_DAYS = {
    SubscriptionTier.INDIE: 14,
    SubscriptionTier.PRO: 90,
    SubscriptionTier.AGENCY: 90,
}


def get_backfill_days(tier: SubscriptionTier) -> int:
    """Get number of backfill days for a subscription tier."""
    return BACKFILL_DAYS.get(tier, 14)


@shared_task(bind=True, max_retries=3)
def historical_backfill(self, product_id: str, days: int | None = None) -> dict[str, Any]:
    """
    Backfill historical mentions for a product.

    This is called when a new product is created to immediately populate
    the feedback dashboard with existing mentions.

    Args:
        product_id: The product to backfill
        days: Override for number of days to backfill (defaults to tier limit)

    Returns:
        Summary of backfill results
    """
    return run_async(_historical_backfill(product_id, days))


async def _historical_backfill(product_id: str, days: int | None = None) -> dict[str, Any]:
    """Async implementation of historical backfill."""
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

        org = product.organization

        # Determine backfill period
        if days is None:
            days = get_backfill_days(org.subscription_tier)

        logger.info(f"Starting historical backfill for {product.name} ({days} days)")

        # Calculate time filter based on days
        if days <= 7:
            time_filter = "week"
        elif days <= 30:
            time_filter = "month"
        else:
            time_filter = "year"

        # Build search queries
        search_queries = product.keywords[:10] + [product.name]

        # Initialize services
        reddit = RedditClient(settings)
        hn = HackerNewsClient()
        ai_router = AIRouter(settings)

        results = {
            "product_id": product_id,
            "product_name": product.name,
            "backfill_days": days,
            "tier": org.subscription_tier.value,
            "sources": {},
        }

        try:
            # =================== Reddit Backfill ===================
            reddit_mentions = []
            for query in search_queries:
                try:
                    posts = await reddit.search_posts(
                        subreddit="all",
                        query=query,
                        time_filter=time_filter,
                        limit=100,  # More results for backfill
                    )
                    reddit_mentions.extend(posts)
                except Exception as e:
                    logger.warning(f"Error searching Reddit for '{query}': {e}")

            # Deduplicate
            seen_ids = set()
            unique_reddit = []
            for m in reddit_mentions:
                if m.get("id") not in seen_ids:
                    seen_ids.add(m.get("id"))
                    unique_reddit.append(m)

            # Filter and analyze
            analyzed_reddit = await _filter_and_analyze_mentions(
                unique_reddit, product, ai_router, "reddit"
            )
            stored_reddit = await _store_feedback_items(
                db, product_id, analyzed_reddit, "reddit"
            )

            results["sources"]["reddit"] = {
                "total_found": len(unique_reddit),
                "relevant": len(analyzed_reddit),
                "stored": stored_reddit,
            }

            # =================== Hacker News Backfill ===================
            hn_mentions = []
            for query in search_queries:
                try:
                    items = await hn.search(
                        query=query,
                        tags="(story,comment)",
                        num_results=100,
                    )
                    hn_mentions.extend(items)
                except Exception as e:
                    logger.warning(f"Error searching HN for '{query}': {e}")

            # Deduplicate
            seen_ids = set()
            unique_hn = []
            for m in hn_mentions:
                item_id = m.get("objectID")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    unique_hn.append(m)

            # Filter and analyze
            analyzed_hn = await _filter_and_analyze_mentions(
                unique_hn, product, ai_router, "hackernews"
            )
            stored_hn = await _store_feedback_items(
                db, product_id, analyzed_hn, "hackernews"
            )

            results["sources"]["hackernews"] = {
                "total_found": len(unique_hn),
                "relevant": len(analyzed_hn),
                "stored": stored_hn,
            }

            # Calculate totals
            total_found = sum(s["total_found"] for s in results["sources"].values())
            total_relevant = sum(s["relevant"] for s in results["sources"].values())
            total_stored = sum(s["stored"] for s in results["sources"].values())

            results["totals"] = {
                "total_found": total_found,
                "total_relevant": total_relevant,
                "total_stored": total_stored,
            }

            logger.info(
                f"Backfill complete for {product.name}: "
                f"found {total_found}, relevant {total_relevant}, stored {total_stored}"
            )

            return results

        finally:
            await reddit.close()
            await hn.close()


@shared_task(bind=True, max_retries=3)
def analyze_feedback_batch(
    self,
    product_id: str,
    feedback_ids: list[str],
) -> dict[str, Any]:
    """
    Re-analyze a batch of feedback items with the EXPENSIVE model.

    Useful for re-processing feedback when AI models improve.
    """
    return run_async(_analyze_feedback_batch(product_id, feedback_ids))


async def _analyze_feedback_batch(
    product_id: str,
    feedback_ids: list[str],
) -> dict[str, Any]:
    """Async implementation of batch analysis."""
    from app.models.feedback import FeedbackItem

    async with async_session_factory() as db:
        # Get product
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()

        if not product:
            return {"error": "Product not found", "product_id": product_id}

        # Get feedback items
        result = await db.execute(
            select(FeedbackItem).where(
                FeedbackItem.id.in_(feedback_ids),
                FeedbackItem.product_id == product_id,
            )
        )
        items = result.scalars().all()

        ai_router = AIRouter(settings)
        product_context = f"{product.name}: {product.description}"
        updated_count = 0

        for item in items:
            try:
                analysis = await ai_router.analyze_sentiment(
                    text=item.text,
                    product_description=product_context,
                )

                # Update item with new analysis
                item.sentiment = analysis.get("sentiment", item.sentiment)
                item.emotion = analysis.get("emotion", item.emotion)
                item.category = analysis.get("category", item.category)
                item.subcategory = analysis.get("subcategory", item.subcategory)
                item.urgency = analysis.get("urgency", item.urgency)
                item.product_area = analysis.get("product_area", item.product_area)
                item.key_phrases = analysis.get("key_phrases", item.key_phrases)
                item.churn_risk = min(1.0, max(0.0, analysis.get("churn_risk", item.churn_risk)))
                item.suggested_action = analysis.get("suggested_action", item.suggested_action)

                updated_count += 1
            except Exception as e:
                logger.error(f"Error re-analyzing feedback {item.id}: {e}")

        await db.commit()

        return {
            "product_id": product_id,
            "requested": len(feedback_ids),
            "found": len(items),
            "updated": updated_count,
        }


@shared_task
def trigger_backfill_for_new_product(product_id: str) -> dict[str, Any]:
    """
    Triggered when a new product is created.

    Determines the appropriate backfill period based on the organization's
    subscription tier and queues the backfill task.
    """
    # Queue the actual backfill task
    task = historical_backfill.delay(product_id)

    return {
        "product_id": product_id,
        "backfill_task_id": task.id,
        "status": "queued",
    }
