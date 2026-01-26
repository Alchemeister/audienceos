"""Tests for the keyword generation service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.models.product import Product
from app.services.keywords import KeywordGenerationService


@pytest.mark.asyncio
class TestKeywordGenerationService:
    """Test the keyword generation service."""

    async def test_generate_keywords_new_product(self):
        """Test generating keywords for a product without keywords."""
        service = KeywordGenerationService()

        # Mock product
        product = Product(
            id=uuid4(),
            name="TaskMaster Pro",
            description="A task management tool for teams",
            url="https://example.com",
            keywords=[],
            competitors=[],
        )

        # Mock AI response
        mock_ai_response = {
            "brand_variations": [
                {"keyword": "TaskMaster", "confidence": 0.9},
                {"keyword": "Task Master", "confidence": 0.8},
            ],
            "founder_team": [],
            "competitors": [
                {"keyword": "Asana", "confidence": 0.95},
                {"keyword": "Trello", "confidence": 0.90},
            ],
            "problem_phrases": [
                {"keyword": "how to manage tasks", "confidence": 0.7},
            ],
            "solution_phrases": [
                {"keyword": "task management software", "confidence": 0.85},
            ],
        }

        with patch.object(
            service.ai_router, "discover_keywords", new_callable=AsyncMock
        ) as mock_discover:
            mock_discover.return_value = mock_ai_response

            # Mock database session
            mock_db = AsyncMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await service.generate_keywords_for_product(
                mock_db, product, force_regenerate=False
            )

            # Assertions
            assert result["action"] == "generated"
            assert result["total_keywords"] > 0
            assert "TaskMaster" in result["keywords"]
            assert "Asana" in result["competitors"]
            assert mock_db.commit.called
            assert mock_db.refresh.called

    async def test_skip_generation_if_keywords_exist(self):
        """Test that generation is skipped if keywords already exist."""
        service = KeywordGenerationService()

        # Mock product with existing keywords
        product = Product(
            id=uuid4(),
            name="TaskMaster Pro",
            description="A task management tool",
            keywords=["task", "management", "productivity"],
            competitors=[],
        )

        mock_db = AsyncMock()

        result = await service.generate_keywords_for_product(
            mock_db, product, force_regenerate=False
        )

        # Should skip
        assert result["action"] == "skipped"
        assert "Keywords already exist" in result["reason"]
        assert not mock_db.commit.called

    async def test_force_regenerate(self):
        """Test force regeneration of keywords."""
        service = KeywordGenerationService()

        # Mock product with existing keywords
        product = Product(
            id=uuid4(),
            name="TaskMaster Pro",
            description="A task management tool",
            keywords=["old", "keywords"],
            competitors=[],
        )

        # Mock AI response
        mock_ai_response = {
            "brand_variations": [
                {"keyword": "TaskMaster", "confidence": 0.9},
            ],
            "founder_team": [],
            "competitors": [],
            "problem_phrases": [],
            "solution_phrases": [],
        }

        with patch.object(
            service.ai_router, "discover_keywords", new_callable=AsyncMock
        ) as mock_discover:
            mock_discover.return_value = mock_ai_response

            mock_db = AsyncMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await service.generate_keywords_for_product(
                mock_db, product, force_regenerate=True
            )

            # Should generate even though keywords exist
            assert result["action"] == "generated"
            assert mock_discover.called

    async def test_update_keywords_add_and_remove(self):
        """Test adding and removing keywords."""
        service = KeywordGenerationService()

        product = Product(
            id=uuid4(),
            name="TaskMaster Pro",
            description="A task management tool",
            keywords=["task", "management", "productivity"],
            competitors=[],
        )

        mock_db = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        result = await service.update_keywords_for_product(
            mock_db,
            product,
            additional_keywords=["agile", "scrum"],
            remove_keywords=["productivity"],
        )

        assert result["action"] == "updated"
        assert "agile" in product.keywords
        assert "scrum" in product.keywords
        assert "productivity" not in product.keywords
        assert mock_db.commit.called

    async def test_analyze_keyword_coverage(self):
        """Test keyword coverage analysis."""
        service = KeywordGenerationService()

        # Product with minimal keywords
        product = Product(
            id=uuid4(),
            name="TaskMaster Pro",
            description="A task management tool",
            keywords=["task"],
            competitors=[],
        )

        analysis = await service.analyze_keyword_coverage(product)

        assert analysis["total_keywords"] == 1
        assert len(analysis["recommendations"]) > 0
        assert any(
            "more keywords" in rec.lower()
            for rec in analysis["recommendations"]
        )

    async def test_keyword_deduplication(self):
        """Test that duplicate keywords are removed."""
        service = KeywordGenerationService()

        product = Product(
            id=uuid4(),
            name="TaskMaster",
            description="Task management",
            keywords=[],
            competitors=[],
        )

        # Mock AI response with duplicates
        mock_ai_response = {
            "brand_variations": [
                {"keyword": "TaskMaster", "confidence": 0.9},
                {"keyword": "taskmaster", "confidence": 0.8},  # Duplicate (case-insensitive)
            ],
            "founder_team": [],
            "competitors": [],
            "problem_phrases": [],
            "solution_phrases": [],
        }

        with patch.object(
            service.ai_router, "discover_keywords", new_callable=AsyncMock
        ) as mock_discover:
            mock_discover.return_value = mock_ai_response

            mock_db = AsyncMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await service.generate_keywords_for_product(
                mock_db, product, force_regenerate=False
            )

            # Should have only one keyword after deduplication
            assert result["total_keywords"] == 1

    async def test_confidence_filtering(self):
        """Test that low-confidence keywords are filtered out."""
        service = KeywordGenerationService()

        product = Product(
            id=uuid4(),
            name="TaskMaster",
            description="Task management",
            keywords=[],
            competitors=[],
        )

        # Mock AI response with low confidence items
        mock_ai_response = {
            "brand_variations": [
                {"keyword": "TaskMaster", "confidence": 0.9},  # High - should include
                {"keyword": "TM", "confidence": 0.3},  # Low - should exclude
            ],
            "founder_team": [],
            "competitors": [],
            "problem_phrases": [],
            "solution_phrases": [],
        }

        with patch.object(
            service.ai_router, "discover_keywords", new_callable=AsyncMock
        ) as mock_discover:
            mock_discover.return_value = mock_ai_response

            mock_db = AsyncMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await service.generate_keywords_for_product(
                mock_db, product, force_regenerate=False
            )

            # Should only include high-confidence keyword
            assert "TaskMaster" in result["keywords"]
            assert "TM" not in result["keywords"]
