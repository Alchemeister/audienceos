"""Enhanced historical backfill tasks with progress tracking and scheduling."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.product import Product
from app.models.user import Organization, SubscriptionTier
from app.services.ai.cached_router import CachedAIRouter
from app.services.research.hackernews import HackerNewsClient
from app.services.research.reddit import RedditClient
from app.tasks.monitoring import (
    _filter_and_analyze_mentions,
    _store_feedback_items,
)

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


# Backfill configurations
BACKFILL_CONFIG = {
    SubscriptionTier.INDIE: {
        "initial_days": 14,
        "max_results_per_query": 50,
        "sources": ["reddit"],
    },
    SubscriptionTier.PRO: {
        "initial_days": 90,
        "max_results_per_query": 100,
        "sources": ["reddit", "hackernews"],
    },
    SubscriptionTier.AGENCY: {
        "initial_days": 180,
        "max_results_per_query": 200,
        "sources": ["reddit", "hackernews"],
    },
}


def get_backfill_config(tier: SubscriptionTier) -> dict[str, Any]:
    """Get backfill configuration for a subscription tier."""
    return BACKFILL_CONFIG.get(tier, BACKFILL_CONFIG[SubscriptionTier.INDIE])


@shared_task(bind=True, max_retries=3)
def enhanced_historical_backfill(
    self,
    product_id: str,
    days: int | None = None,
    sources: list[str] | None = None,
) -> dict[str, Any]:
    """
    Enhanced historical backfill with progress tracking and rate limit handling.

    Features:
    - Progress tracking via task state
    - Intelligent rate limit handling
    - Configurable sources
    - Deduplication across runs
    - Detailed statistics

    Args:
        product_id: The product to backfill
        days: Override for number of days to backfill
        sources: Override for sources to backfill from

    Returns:
        Detailed backfill results with statistics
    """
    return run_async(_enhanced_historical_backfill(self, product_id, days, sources))


async def _enhanced_historical_backfill(
    task,
    product_id: str,
    days: int | None = None,
    sources: list[str] | None = None,
) -> dict[str, Any]:
    """Async implementation of enhanced historical backfill."""
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
        config = get_backfill_config(org.subscription_tier)

        # Determine parameters
        days = days or config["initial_days"]
        sources = sources or config["sources"]
        max_results = config["max_results_per_query"]

        logger.info(
            f"Starting enhanced backfill for {product.name} "
            f"(tier: {org.subscription_tier.value}, days: {days}, sources: {sources})"
        )

        # Update task state
        task.update_state(
            state="PROGRESS",
            meta={
                "product_id": product_id,
                "product_name": product.name,
                "stage": "initializing",
                "progress": 0,
            },
        )

        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # Build search queries (prioritize keywords, then product name)
        search_queries = []
        if product.keywords:
            search_queries.extend(product.keywords[:15])  # Top 15 keywords
        search_queries.append(product.name)

        # Deduplicate
        search_queries = list(dict.fromkeys(search_queries))

        # Initialize services
        reddit = RedditClient(settings) if "reddit" in sources else None
        hn = HackerNewsClient() if "hackernews" in sources else None
        ai_router = CachedAIRouter(settings)

        results = {
            "product_id": product_id,
            "product_name": product.name,
            "backfill_days": days,
            "tier": org.subscription_tier.value,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "search_queries": search_queries,
            "sources": {},
            "errors": [],
        }

        total_steps = len(sources) * len(search_queries)
        current_step = 0

        try:
            # =================== Reddit Backfill ===================
            if reddit:
                task.update_state(
                    state="PROGRESS",
                    meta={
                        "product_id": product_id,
                        "product_name": product.name,
                        "stage": "reddit_backfill",
                        "progress": int((current_step / total_steps) * 100),
                    },
                )

                reddit_mentions = []
                reddit_errors = []

                for query in search_queries:
                    try:
                        # Determine time filter
                        if days <= 7:
                            time_filter = "week"
                        elif days <= 30:
                            time_filter = "month"
                        elif days <= 365:
                            time_filter = "year"
                        else:
                            time_filter = "all"

                        posts = await reddit.search_posts(
                            subreddit="all",
                            query=query,
                            time_filter=time_filter,
                            limit=max_results,
                        )
                        reddit_mentions.extend(posts)

                    except Exception as e:
                        error_msg = f"Reddit search error for '{query}': {str(e)}"
                        logger.warning(error_msg)
                        reddit_errors.append(error_msg)

                    current_step += 1
                    task.update_state(
                        state="PROGRESS",
                        meta={
                            "product_id": product_id,
                            "product_name": product.name,
                            "stage": "reddit_backfill",
                            "progress": int((current_step / total_steps) * 100),
                            "current_query": query,
                        },
                    )

                # Deduplicate by ID
                seen_ids = set()
                unique_reddit = []
                for m in reddit_mentions:
                    post_id = m.get("id")
                    if post_id and post_id not in seen_ids:
                        seen_ids.add(post_id)
                        unique_reddit.append(m)

                # Filter time range
                filtered_reddit = [
                    m
                    for m in unique_reddit
                    if start_time.timestamp()
                    <= m.get("created_utc", 0)
                    <= end_time.timestamp()
                ]

                # Analyze (with caching!)
                analyzed_reddit = await _filter_and_analyze_mentions(
                    filtered_reddit, product, ai_router, "reddit"
                )

                # Store
                stored_reddit = await _store_feedback_items(
                    db, product_id, analyzed_reddit, "reddit"
                )

                results["sources"]["reddit"] = {
                    "total_found": len(reddit_mentions),
                    "unique": len(unique_reddit),
                    "in_time_range": len(filtered_reddit),
                    "relevant": len(analyzed_reddit),
                    "stored": stored_reddit,
                    "errors": reddit_errors,
                }

            # =================== Hacker News Backfill ===================
            if hn:
                task.update_state(
                    state="PROGRESS",
                    meta={
                        "product_id": product_id,
                        "product_name": product.name,
                        "stage": "hackernews_backfill",
                        "progress": int((current_step / total_steps) * 100),
                    },
                )

                hn_mentions = []
                hn_errors = []

                for query in search_queries:
                    try:
                        items = await hn.search(
                            query=query,
                            tags="(story,comment)",
                            num_results=max_results,
                        )
                        hn_mentions.extend(items)

                    except Exception as e:
                        error_msg = f"HN search error for '{query}': {str(e)}"
                        logger.warning(error_msg)
                        hn_errors.append(error_msg)

                    current_step += 1
                    task.update_state(
                        state="PROGRESS",
                        meta={
                            "product_id": product_id,
                            "product_name": product.name,
                            "stage": "hackernews_backfill",
                            "progress": int((current_step / total_steps) * 100),
                            "current_query": query,
                        },
                    )

                # Deduplicate by objectID
                seen_ids = set()
                unique_hn = []
                for m in hn_mentions:
                    item_id = m.get("objectID")
                    if item_id and item_id not in seen_ids:
                        seen_ids.add(item_id)
                        unique_hn.append(m)

                # Filter time range
                filtered_hn = [
                    m
                    for m in unique_hn
                    if m.get("created_at_i")
                    and start_time.timestamp()
                    <= m.get("created_at_i", 0)
                    <= end_time.timestamp()
                ]

                # Analyze (with caching!)
                analyzed_hn = await _filter_and_analyze_mentions(
                    filtered_hn, product, ai_router, "hackernews"
                )

                # Store
                stored_hn = await _store_feedback_items(
                    db, product_id, analyzed_hn, "hackernews"
                )

                results["sources"]["hackernews"] = {
                    "total_found": len(hn_mentions),
                    "unique": len(unique_hn),
                    "in_time_range": len(filtered_hn),
                    "relevant": len(analyzed_hn),
                    "stored": stored_hn,
                    "errors": hn_errors,
                }

            # Calculate totals
            total_found = sum(s.get("total_found", 0) for s in results["sources"].values())
            total_relevant = sum(s.get("relevant", 0) for s in results["sources"].values())
            total_stored = sum(s.get("stored", 0) for s in results["sources"].values())

            results["totals"] = {
                "total_found": total_found,
                "total_unique": sum(
                    s.get("unique", 0) for s in results["sources"].values()
                ),
                "in_time_range": sum(
                    s.get("in_time_range", 0) for s in results["sources"].values()
                ),
                "total_relevant": total_relevant,
                "total_stored": total_stored,
                "relevance_rate": (
                    round((total_relevant / total_found) * 100, 2)
                    if total_found > 0
                    else 0.0
                ),
            }

            # Update product backfill timestamp
            product.backfill_completed_at = datetime.utcnow()
            await db.commit()

            logger.info(
                f"Enhanced backfill complete for {product.name}: "
                f"found {total_found}, relevant {total_relevant}, stored {total_stored}"
            )

            # Final state update
            task.update_state(
                state="SUCCESS",
                meta={
                    "product_id": product_id,
                    "product_name": product.name,
                    "stage": "complete",
                    "progress": 100,
                    "results": results,
                },
            )

            return results

        finally:
            if reddit:
                await reddit.close()
            if hn:
                await hn.close()


@shared_task(bind=True)
def scheduled_incremental_backfill(self) -> dict[str, Any]:
    """
    Scheduled task to catch up on missed mentions for all products.

    Runs daily to fill gaps in monitoring (e.g., during downtime).
    Only processes mentions from the last 7 days to avoid duplicates.
    """
    return run_async(_scheduled_incremental_backfill())


async def _scheduled_incremental_backfill() -> dict[str, Any]:
    """
    Async implementation of incremental backfill.

    Processes all active products that haven't been monitored recently.
    """
    async with async_session_factory() as db:
        # Get all products that haven't been checked in the last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)

        result = await db.execute(
            select(Product)
            .where(
                (Product.feedback_last_collected_at < cutoff)
                | (Product.feedback_last_collected_at.is_(None))
            )
            .options(selectinload(Product.organization))
        )
        products = result.scalars().all()

        logger.info(
            f"Starting incremental backfill for {len(products)} products"
        )

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "products_processed": 0,
            "total_mentions_found": 0,
            "total_stored": 0,
            "products": [],
        }

        for product in products:
            try:
                # Backfill last 7 days only
                backfill_result = await _enhanced_historical_backfill(
                    self,
                    str(product.id),
                    days=7,
                    sources=["reddit", "hackernews"],
                )

                results["products"].append({
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "mentions_found": backfill_result.get("totals", {}).get(
                        "total_found", 0
                    ),
                    "stored": backfill_result.get("totals", {}).get("total_stored", 0),
                })

                results["products_processed"] += 1
                results["total_mentions_found"] += backfill_result.get("totals", {}).get(
                    "total_found", 0
                )
                results["total_stored"] += backfill_result.get("totals", {}).get(
                    "total_stored", 0
                )

            except Exception as e:
                logger.error(f"Error in incremental backfill for {product.name}: {e}")
                results["products"].append({
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "error": str(e),
                })

        logger.info(
            f"Incremental backfill complete: "
            f"processed {results['products_processed']} products, "
            f"stored {results['total_stored']} mentions"
        )

        return results


@shared_task
def trigger_backfill_for_new_product(product_id: str) -> dict[str, Any]:
    """
    Triggered when a new product is created.

    Uses the enhanced backfill with progress tracking.
    """
    task = enhanced_historical_backfill.delay(product_id)

    return {
        "product_id": product_id,
        "backfill_task_id": task.id,
        "status": "queued",
        "message": "Enhanced backfill queued with progress tracking",
    }
