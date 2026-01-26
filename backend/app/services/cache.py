"""Redis caching service for expensive AI operations."""

import hashlib
import json
import logging
from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheService:
    """
    Redis-based caching service for AI operations.

    Caches expensive AI API calls to reduce costs and improve response times.
    Uses content-based hashing for cache keys to ensure consistency.
    """

    def __init__(self):
        """Initialize the cache service."""
        self._redis: redis.Redis | None = None

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    def _generate_cache_key(
        self,
        operation: str,
        **kwargs: Any,
    ) -> str:
        """
        Generate a deterministic cache key based on operation and parameters.

        Args:
            operation: Name of the AI operation (e.g., 'sentiment_analysis')
            **kwargs: Parameters that affect the result

        Returns:
            Cache key string
        """
        # Sort kwargs for deterministic hashing
        sorted_params = json.dumps(kwargs, sort_keys=True)
        param_hash = hashlib.sha256(sorted_params.encode()).hexdigest()[:16]

        return f"ai_cache:{operation}:{param_hash}"

    async def get_cached_result(
        self,
        operation: str,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """
        Get a cached AI operation result.

        Args:
            operation: Name of the AI operation
            **kwargs: Parameters that were used for the operation

        Returns:
            Cached result dict or None if not found/expired
        """
        try:
            redis_client = await self._get_redis()
            cache_key = self._generate_cache_key(operation, **kwargs)

            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache HIT for {operation}")
                return json.loads(cached)

            logger.debug(f"Cache MISS for {operation}")
            return None

        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    async def cache_result(
        self,
        operation: str,
        result: dict[str, Any],
        ttl_seconds: int = 86400,  # 24 hours default
        **kwargs: Any,
    ) -> bool:
        """
        Cache an AI operation result.

        Args:
            operation: Name of the AI operation
            result: Result to cache
            ttl_seconds: Time to live in seconds (default 24h)
            **kwargs: Parameters that were used for the operation

        Returns:
            True if cached successfully, False otherwise
        """
        try:
            redis_client = await self._get_redis()
            cache_key = self._generate_cache_key(operation, **kwargs)

            await redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(result),
            )

            logger.info(f"Cached result for {operation} (TTL: {ttl_seconds}s)")
            return True

        except Exception as e:
            logger.error(f"Cache write error: {e}")
            return False

    async def invalidate_cache(
        self,
        operation: str,
        **kwargs: Any,
    ) -> bool:
        """
        Invalidate a specific cache entry.

        Args:
            operation: Name of the AI operation
            **kwargs: Parameters that were used for the operation

        Returns:
            True if invalidated successfully, False otherwise
        """
        try:
            redis_client = await self._get_redis()
            cache_key = self._generate_cache_key(operation, **kwargs)

            deleted = await redis_client.delete(cache_key)
            logger.info(f"Invalidated cache for {operation}")
            return deleted > 0

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    async def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats (keys, memory, hits, etc.)
        """
        try:
            redis_client = await self._get_redis()

            # Get info
            info = await redis_client.info("stats")

            # Count AI cache keys
            ai_keys = 0
            async for key in redis_client.scan_iter(match="ai_cache:*"):
                ai_keys += 1

            return {
                "total_ai_cache_keys": ai_keys,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate percentage."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses

        if total == 0:
            return 0.0

        return round((hits / total) * 100, 2)

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None


# TTL configurations for different operation types
CACHE_TTL = {
    # Long-lived caches (relatively stable results)
    "keyword_discovery": 7 * 24 * 3600,  # 7 days
    "audience_research": 7 * 24 * 3600,  # 7 days
    "content_generation": 3 * 24 * 3600,  # 3 days

    # Medium-lived caches
    "sentiment_analysis": 24 * 3600,  # 24 hours
    "feedback_analysis_bulk": 24 * 3600,  # 24 hours
    "theme_clustering": 12 * 3600,  # 12 hours

    # Short-lived caches (frequently changing)
    "weekly_report": 3600,  # 1 hour
    "relevance_filter": 6 * 3600,  # 6 hours
}


def get_cache_ttl(operation: str) -> int:
    """Get TTL for a specific operation type."""
    return CACHE_TTL.get(operation, 24 * 3600)  # Default 24 hours


# Global cache instance
_cache_instance: CacheService | None = None


async def get_cache_service() -> CacheService:
    """Get or create the global cache service instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance
