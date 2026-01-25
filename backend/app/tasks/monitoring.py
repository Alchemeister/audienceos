"""Background monitoring tasks for Reddit and Hacker News mentions."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.feedback import FeedbackCategory, FeedbackItem, Sentiment, Urgency
from app.models.product import Product
from app.models.user import Organization, SubscriptionTier
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


async def _get_product_with_org(db: AsyncSession, product_id: str) -> tuple[Product, Organization] | None:
    """Get product with its organization."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.organization))
    )
    product = result.scalar_one_or_none()
    if not product:
        return None
    return product, product.organization


async def _filter_and_analyze_mentions(
    mentions: list[dict[str, Any]],
    product: Product,
    ai_router: AIRouter,
    source: str,
) -> list[dict[str, Any]]:
    """
    Tiered analysis pipeline:
    1. CHEAP model filters for relevance
    2. EXPENSIVE model analyzes relevant mentions

    Flow: 1000 raw mentions → cheap filters to ~150 relevant → expensive analyzes
    """
    if not mentions:
        return []

    # Step 1: Filter with CHEAP model
    logger.info(f"Filtering {len(mentions)} {source} mentions for {product.name}")

    texts = [f"{m.get('title', '')} {m.get('text', m.get('selftext', ''))}".strip() for m in mentions]
    keywords = product.keywords + [product.name]

    try:
        relevance_results = await ai_router.filter_relevance(
            texts=texts,
            product_name=product.name,
            keywords=keywords,
        )
    except Exception as e:
        logger.error(f"Error filtering mentions: {e}")
        # On AI failure, do basic keyword matching as fallback
        relevance_results = [
            {"is_relevant": any(kw.lower() in text.lower() for kw in keywords), "confidence": 0.5}
            for text in texts
        ]

    # Filter to relevant mentions
    relevant_mentions = []
    for mention, result in zip(mentions, relevance_results):
        if result.get("is_relevant", False) and result.get("confidence", 0) >= 0.5:
            mention["_relevance"] = result
            relevant_mentions.append(mention)

    logger.info(f"Found {len(relevant_mentions)} relevant mentions out of {len(mentions)}")

    if not relevant_mentions:
        return []

    # Step 2: Analyze with EXPENSIVE model
    analyzed_mentions = []
    product_context = f"{product.name}: {product.description}"

    for mention in relevant_mentions:
        text = f"{mention.get('title', '')} {mention.get('text', mention.get('selftext', ''))}".strip()

        try:
            analysis = await ai_router.analyze_sentiment(
                text=text,
                product_description=product_context,
            )
            mention["_analysis"] = analysis
            analyzed_mentions.append(mention)
        except Exception as e:
            logger.error(f"Error analyzing mention: {e}")
            # Use basic classification as fallback
            try:
                classification = await ai_router.classify_feedback(text)
                mention["_analysis"] = {
                    "sentiment": "neutral",
                    "category": classification.get("category", "question"),
                    "urgency": "medium",
                    "key_phrases": [],
                    "churn_risk": 0.0,
                }
                analyzed_mentions.append(mention)
            except Exception:
                pass  # Skip this mention entirely

    return analyzed_mentions


async def _store_feedback_items(
    db: AsyncSession,
    product_id: str,
    analyzed_mentions: list[dict[str, Any]],
    source: str,
) -> int:
    """Store analyzed mentions as FeedbackItems."""
    stored_count = 0

    for mention in analyzed_mentions:
        analysis = mention.get("_analysis", {})

        # Build source URL
        source_url = mention.get("url") or mention.get("permalink")
        if source_url and not source_url.startswith("http"):
            if source == "reddit":
                source_url = f"https://reddit.com{source_url}"
            elif source == "hackernews":
                source_url = f"https://news.ycombinator.com/item?id={mention.get('objectID', mention.get('id', ''))}"

        # Check for duplicate (same source_url)
        if source_url:
            existing = await db.execute(
                select(FeedbackItem).where(
                    FeedbackItem.product_id == product_id,
                    FeedbackItem.source_url == source_url,
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicate

        # Create FeedbackItem
        text = f"{mention.get('title', '')} {mention.get('text', mention.get('selftext', ''))}".strip()

        feedback_item = FeedbackItem(
            product_id=product_id,
            source=source,
            source_url=source_url,
            author=mention.get("author") or mention.get("by"),
            author_id=mention.get("author_id"),
            text=text[:10000],  # Limit text length
            sentiment=analysis.get("sentiment", "neutral"),
            emotion=analysis.get("emotion"),
            category=analysis.get("category", "question"),
            subcategory=analysis.get("subcategory"),
            urgency=analysis.get("urgency", "medium"),
            product_area=analysis.get("product_area"),
            key_phrases=analysis.get("key_phrases", []),
            churn_risk=min(1.0, max(0.0, analysis.get("churn_risk", 0.0))),
            suggested_action=analysis.get("suggested_action"),
            raw_data={
                "source_data": {k: v for k, v in mention.items() if not k.startswith("_")},
                "relevance": mention.get("_relevance", {}),
            },
            collected_at=datetime.utcnow(),
        )

        db.add(feedback_item)
        stored_count += 1

    if stored_count > 0:
        await db.commit()

    return stored_count


@shared_task(bind=True, max_retries=3)
def monitor_reddit_mentions(self, product_id: str) -> dict[str, Any]:
    """
    Monitor Reddit for mentions of a product.

    Searches Reddit using product keywords and name, then filters
    and analyzes mentions using the tiered AI pipeline.
    """
    return run_async(_monitor_reddit_mentions(product_id))


async def _monitor_reddit_mentions(product_id: str) -> dict[str, Any]:
    """Async implementation of Reddit monitoring."""
    async with async_session_factory() as db:
        result = await _get_product_with_org(db, product_id)
        if not result:
            return {"error": "Product not found", "product_id": product_id}

        product, org = result

        # Build search queries from keywords
        search_queries = product.keywords[:5] + [product.name]  # Limit queries

        # Initialize clients
        reddit = RedditClient(settings)
        ai_router = AIRouter(settings)

        all_mentions = []

        try:
            # Search for each keyword in relevant subreddits
            for query in search_queries:
                try:
                    # Search across Reddit
                    posts = await reddit.search_posts(
                        subreddit="all",
                        query=query,
                        time_filter="week",  # Last week for regular monitoring
                        limit=25,
                    )
                    all_mentions.extend(posts)
                except Exception as e:
                    logger.warning(f"Error searching Reddit for '{query}': {e}")

            # Deduplicate by post ID
            seen_ids = set()
            unique_mentions = []
            for mention in all_mentions:
                post_id = mention.get("id")
                if post_id and post_id not in seen_ids:
                    seen_ids.add(post_id)
                    unique_mentions.append(mention)

            # Filter and analyze
            analyzed = await _filter_and_analyze_mentions(
                unique_mentions, product, ai_router, "reddit"
            )

            # Store results
            stored = await _store_feedback_items(db, product_id, analyzed, "reddit")

            return {
                "product_id": product_id,
                "product_name": product.name,
                "source": "reddit",
                "total_found": len(unique_mentions),
                "relevant": len(analyzed),
                "stored": stored,
            }

        finally:
            await reddit.close()


@shared_task(bind=True, max_retries=3)
def monitor_hackernews_mentions(self, product_id: str) -> dict[str, Any]:
    """Monitor Hacker News for mentions of a product."""
    return run_async(_monitor_hackernews_mentions(product_id))


async def _monitor_hackernews_mentions(product_id: str) -> dict[str, Any]:
    """Async implementation of Hacker News monitoring."""
    async with async_session_factory() as db:
        result = await _get_product_with_org(db, product_id)
        if not result:
            return {"error": "Product not found", "product_id": product_id}

        product, org = result

        # Build search queries
        search_queries = product.keywords[:5] + [product.name]

        # Initialize clients
        hn = HackerNewsClient()
        ai_router = AIRouter(settings)

        all_mentions = []

        try:
            for query in search_queries:
                try:
                    items = await hn.search(
                        query=query,
                        tags="(story,comment)",
                        num_results=25,
                    )
                    all_mentions.extend(items)
                except Exception as e:
                    logger.warning(f"Error searching HN for '{query}': {e}")

            # Deduplicate
            seen_ids = set()
            unique_mentions = []
            for mention in all_mentions:
                item_id = mention.get("objectID")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    unique_mentions.append(mention)

            # Filter and analyze
            analyzed = await _filter_and_analyze_mentions(
                unique_mentions, product, ai_router, "hackernews"
            )

            # Store results
            stored = await _store_feedback_items(db, product_id, analyzed, "hackernews")

            return {
                "product_id": product_id,
                "product_name": product.name,
                "source": "hackernews",
                "total_found": len(unique_mentions),
                "relevant": len(analyzed),
                "stored": stored,
            }

        finally:
            await hn.close()


@shared_task
def monitor_all_products() -> dict[str, Any]:
    """
    Periodic task to monitor mentions for all active products.

    Scheduled by Celery Beat to run every 15 minutes.
    """
    return run_async(_monitor_all_products())


async def _monitor_all_products() -> dict[str, Any]:
    """Async implementation of monitoring all products."""
    async with async_session_factory() as db:
        # Get all products
        result = await db.execute(select(Product))
        products = result.scalars().all()

        results = []
        for product in products:
            # Queue individual monitoring tasks
            monitor_reddit_mentions.delay(str(product.id))
            monitor_hackernews_mentions.delay(str(product.id))
            results.append(str(product.id))

        return {
            "products_queued": len(results),
            "product_ids": results,
        }


@shared_task
def cleanup_old_events(days: int = 90) -> dict[str, Any]:
    """Clean up old click events older than specified days."""
    return run_async(_cleanup_old_events(days))


async def _cleanup_old_events(days: int) -> dict[str, Any]:
    """Async implementation of cleanup."""
    from app.models.campaign import ClickEvent

    async with async_session_factory() as db:
        cutoff = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(ClickEvent).where(ClickEvent.clicked_at < cutoff)
        )
        old_events = result.scalars().all()
        count = len(old_events)

        for event in old_events:
            await db.delete(event)

        await db.commit()

        return {"deleted": count, "cutoff_date": cutoff.isoformat()}
