"""Cached AI router wrapper for cost optimization."""

import logging
from typing import Any

from app.core.config import Settings
from app.services.ai.router import AIRouter, ModelTier
from app.services.cache import get_cache_service, get_cache_ttl

logger = logging.getLogger(__name__)


class CachedAIRouter(AIRouter):
    """
    AI Router with Redis caching for expensive operations.

    Wraps the standard AIRouter and caches results to minimize API calls.
    Particularly valuable for:
    - Repeated sentiment analysis of the same text
    - Audience research for similar product descriptions
    - Keyword discovery for products in the same category
    """

    def __init__(self, settings: Settings):
        """Initialize cached AI router."""
        super().__init__(settings)
        self._cache_enabled = bool(settings.REDIS_URL)

    async def _get_cached_or_compute(
        self,
        operation: str,
        compute_func,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get result from cache or compute if not cached.

        Args:
            operation: Name of the operation for cache keying
            compute_func: Async function to call if cache miss
            **kwargs: Arguments for the compute function and cache key

        Returns:
            The result (from cache or freshly computed)
        """
        if not self._cache_enabled:
            return await compute_func()

        cache = await get_cache_service()

        # Try to get from cache
        cached_result = await cache.get_cached_result(operation, **kwargs)
        if cached_result is not None:
            return cached_result

        # Cache miss - compute the result
        result = await compute_func()

        # Cache the result
        ttl = get_cache_ttl(operation)
        await cache.cache_result(operation, result, ttl_seconds=ttl, **kwargs)

        return result

    # =========================================================================
    # CHEAP TIER - Cached operations
    # =========================================================================

    async def analyze_feedback_bulk(
        self,
        text: str,
        product_description: str,
    ) -> dict[str, Any]:
        """
        Analyze feedback with caching.

        Cache key includes text and product description.
        TTL: 24 hours (sentiment doesn't change for same text).
        """
        return await self._get_cached_or_compute(
            operation="feedback_analysis_bulk",
            compute_func=lambda: super(CachedAIRouter, self).analyze_feedback_bulk(
                text, product_description
            ),
            text=text,
            product_description=product_description,
        )

    async def classify_feedback(self, text: str) -> dict[str, Any]:
        """
        Classify feedback with caching.

        Cache key includes text only.
        TTL: 24 hours.
        """
        return await self._get_cached_or_compute(
            operation="classify_feedback",
            compute_func=lambda: super(CachedAIRouter, self).classify_feedback(text),
            text=text,
        )

    # =========================================================================
    # EXPENSIVE TIER - Heavily cached operations
    # =========================================================================

    async def discover_keywords(
        self,
        product_name: str,
        product_description: str,
        product_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Discover keywords with caching.

        Cache key includes product details.
        TTL: 7 days (keywords for a product don't change frequently).
        """
        return await self._get_cached_or_compute(
            operation="keyword_discovery",
            compute_func=lambda: super(CachedAIRouter, self).discover_keywords(
                product_name, product_description, product_url
            ),
            product_name=product_name,
            product_description=product_description,
            product_url=product_url or "",
        )

    async def research_audience(
        self,
        product_description: str,
    ) -> dict[str, Any]:
        """
        Research audience with caching.

        Cache key includes product description.
        TTL: 7 days (audience locations are relatively stable).
        """
        return await self._get_cached_or_compute(
            operation="audience_research",
            compute_func=lambda: super(CachedAIRouter, self).research_audience(
                product_description
            ),
            product_description=product_description,
        )

    async def generate_content(
        self,
        subreddit: str,
        rules: str,
        topic: str,
        product_context: str,
    ) -> dict[str, Any]:
        """
        Generate content with caching.

        Cache key includes all generation parameters.
        TTL: 3 days (content can be reused for similar requests).
        """
        return await self._get_cached_or_compute(
            operation="content_generation",
            compute_func=lambda: super(CachedAIRouter, self).generate_content(
                subreddit, rules, topic, product_context
            ),
            subreddit=subreddit,
            rules=rules,
            topic=topic,
            product_context=product_context,
        )

    async def analyze_sentiment_deep(
        self,
        text: str,
        product_description: str,
    ) -> dict[str, Any]:
        """
        Deep sentiment analysis with caching.

        Cache key includes text and product description.
        TTL: 24 hours.
        """
        return await self._get_cached_or_compute(
            operation="sentiment_analysis",
            compute_func=lambda: super(CachedAIRouter, self).analyze_sentiment_deep(
                text, product_description
            ),
            text=text,
            product_description=product_description,
        )

    async def cluster_themes(
        self,
        product_name: str,
        product_description: str,
        feedback_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Cluster themes with caching.

        Cache key includes product and a hash of feedback items.
        TTL: 12 hours (themes change as new feedback arrives).

        Note: We create a simplified representation for the cache key.
        """
        # Create a cache-friendly representation of feedback items
        feedback_summary = [
            {
                "text": item.get("text", "")[:100],  # First 100 chars
                "sentiment": item.get("sentiment"),
                "category": item.get("category"),
            }
            for item in feedback_items[:50]  # Limit to first 50 for cache key
        ]

        return await self._get_cached_or_compute(
            operation="theme_clustering",
            compute_func=lambda: super(CachedAIRouter, self).cluster_themes(
                product_name, product_description, feedback_items
            ),
            product_name=product_name,
            product_description=product_description,
            feedback_count=len(feedback_items),
            feedback_summary=str(feedback_summary),  # Simplified for caching
        )

    # =========================================================================
    # Cache management
    # =========================================================================

    async def invalidate_product_cache(self, product_id: str) -> None:
        """
        Invalidate all cache entries for a product.

        Useful when product description changes significantly.

        Args:
            product_id: ID of the product to invalidate cache for
        """
        if not self._cache_enabled:
            return

        cache = await get_cache_service()

        logger.info(f"Invalidating cache for product {product_id}")
        # Note: This is a simplified version. In production, you might
        # want to track which cache entries belong to which products
        # for more precise invalidation.

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        if not self._cache_enabled:
            return {"cache_enabled": False}

        cache = await get_cache_service()
        stats = await cache.get_cache_stats()
        stats["cache_enabled"] = True

        return stats
