"""Tests for the cache service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.cache import CacheService, get_cache_ttl


@pytest.mark.asyncio
class TestCacheService:
    """Test the Redis caching service."""

    async def test_generate_cache_key_deterministic(self):
        """Test that cache keys are deterministic."""
        cache = CacheService()

        key1 = cache._generate_cache_key(
            "sentiment_analysis",
            text="Hello world",
            product="Test Product",
        )

        key2 = cache._generate_cache_key(
            "sentiment_analysis",
            text="Hello world",
            product="Test Product",
        )

        assert key1 == key2

    async def test_generate_cache_key_order_independent(self):
        """Test that parameter order doesn't affect cache key."""
        cache = CacheService()

        key1 = cache._generate_cache_key(
            "sentiment_analysis",
            text="Hello",
            product="Test",
        )

        key2 = cache._generate_cache_key(
            "sentiment_analysis",
            product="Test",
            text="Hello",
        )

        assert key1 == key2

    async def test_generate_cache_key_unique_for_different_params(self):
        """Test that different parameters produce different keys."""
        cache = CacheService()

        key1 = cache._generate_cache_key(
            "sentiment_analysis",
            text="Hello world",
        )

        key2 = cache._generate_cache_key(
            "sentiment_analysis",
            text="Different text",
        )

        assert key1 != key2

    async def test_cache_result_and_get(self):
        """Test caching and retrieving results."""
        with patch("app.services.cache.redis") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url = AsyncMock(return_value=mock_client)

            cache = CacheService()

            # Cache a result
            result = {"sentiment": "positive", "confidence": 0.95}
            success = await cache.cache_result(
                "sentiment_analysis",
                result,
                ttl_seconds=3600,
                text="Great product!",
            )

            assert success is True
            mock_client.setex.assert_called_once()

    async def test_get_cached_result_hit(self):
        """Test cache hit scenario."""
        with patch("app.services.cache.redis") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url = AsyncMock(return_value=mock_client)

            # Mock a cache hit
            cached_data = '{"sentiment": "positive", "confidence": 0.95}'
            mock_client.get = AsyncMock(return_value=cached_data)

            cache = CacheService()

            result = await cache.get_cached_result(
                "sentiment_analysis",
                text="Great product!",
            )

            assert result is not None
            assert result["sentiment"] == "positive"
            assert result["confidence"] == 0.95

    async def test_get_cached_result_miss(self):
        """Test cache miss scenario."""
        with patch("app.services.cache.redis") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url = AsyncMock(return_value=mock_client)

            # Mock a cache miss
            mock_client.get = AsyncMock(return_value=None)

            cache = CacheService()

            result = await cache.get_cached_result(
                "sentiment_analysis",
                text="Great product!",
            )

            assert result is None

    async def test_invalidate_cache(self):
        """Test cache invalidation."""
        with patch("app.services.cache.redis") as mock_redis:
            mock_client = AsyncMock()
            mock_redis.from_url = AsyncMock(return_value=mock_client)
            mock_client.delete = AsyncMock(return_value=1)

            cache = CacheService()

            success = await cache.invalidate_cache(
                "sentiment_analysis",
                text="Great product!",
            )

            assert success is True
            mock_client.delete.assert_called_once()

    def test_get_cache_ttl_known_operation(self):
        """Test getting TTL for known operations."""
        ttl = get_cache_ttl("keyword_discovery")
        assert ttl == 7 * 24 * 3600  # 7 days

        ttl = get_cache_ttl("sentiment_analysis")
        assert ttl == 24 * 3600  # 24 hours

    def test_get_cache_ttl_unknown_operation(self):
        """Test getting TTL for unknown operations (should use default)."""
        ttl = get_cache_ttl("unknown_operation")
        assert ttl == 24 * 3600  # Default 24 hours
