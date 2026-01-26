"""Automatic keyword generation service."""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.product import Product
from app.services.ai.cached_router import CachedAIRouter

logger = logging.getLogger(__name__)
settings = get_settings()


class KeywordGenerationService:
    """
    Service for automatic keyword generation and management.

    Generates comprehensive keywords for products to improve monitoring coverage.
    """

    def __init__(self):
        """Initialize the keyword generation service."""
        self.ai_router = CachedAIRouter(settings)

    async def generate_keywords_for_product(
        self,
        db: AsyncSession,
        product: Product,
        force_regenerate: bool = False,
    ) -> dict[str, Any]:
        """
        Generate or update keywords for a product.

        Args:
            db: Database session
            product: Product to generate keywords for
            force_regenerate: Force regeneration even if keywords exist

        Returns:
            Dictionary with generation results and statistics
        """
        # Check if product already has keywords
        if product.keywords and not force_regenerate:
            logger.info(
                f"Product {product.id} already has {len(product.keywords)} keywords, skipping"
            )
            return {
                "product_id": str(product.id),
                "product_name": product.name,
                "action": "skipped",
                "reason": "Keywords already exist (use force_regenerate=True to override)",
                "existing_keywords": product.keywords,
            }

        logger.info(f"Generating keywords for product: {product.name}")

        try:
            # Call AI to discover keywords
            keyword_data = await self.ai_router.discover_keywords(
                product_name=product.name,
                product_description=product.description,
                product_url=product.url,
            )

            # Extract and flatten keywords from different categories
            all_keywords = []
            category_counts = {}

            # Process each category
            categories = [
                "brand_variations",
                "founder_team",
                "competitors",
                "problem_phrases",
                "solution_phrases",
            ]

            for category in categories:
                category_keywords = keyword_data.get(category, [])

                # Each keyword might be a dict with "keyword" and "confidence"
                # or just a string
                extracted = []
                for item in category_keywords:
                    if isinstance(item, dict):
                        keyword = item.get("keyword", "")
                        confidence = item.get("confidence", 0.0)

                        # Only include high-confidence keywords (>0.5)
                        if confidence > 0.5 and keyword:
                            extracted.append(keyword)
                    elif isinstance(item, str):
                        extracted.append(item)

                all_keywords.extend(extracted)
                category_counts[category] = len(extracted)

            # Deduplicate while preserving order
            seen = set()
            unique_keywords = []
            for kw in all_keywords:
                kw_lower = kw.lower()
                if kw_lower not in seen:
                    seen.add(kw_lower)
                    unique_keywords.append(kw)

            # Update product keywords
            product.keywords = unique_keywords

            # Update competitors list from discovered competitors
            competitors = keyword_data.get("competitors", [])
            if competitors:
                competitor_names = [
                    c.get("keyword", c) if isinstance(c, dict) else c
                    for c in competitors
                ]
                product.competitors = competitor_names[:10]  # Limit to top 10

            await db.commit()
            await db.refresh(product)

            logger.info(
                f"Generated {len(unique_keywords)} keywords for {product.name}"
            )

            return {
                "product_id": str(product.id),
                "product_name": product.name,
                "action": "generated",
                "total_keywords": len(unique_keywords),
                "keywords": unique_keywords,
                "category_breakdown": category_counts,
                "competitors_discovered": len(product.competitors),
                "competitors": product.competitors,
            }

        except Exception as e:
            logger.error(f"Error generating keywords for {product.name}: {e}")
            raise

    async def update_keywords_for_product(
        self,
        db: AsyncSession,
        product: Product,
        additional_keywords: list[str] | None = None,
        remove_keywords: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Update keywords for a product (add or remove specific keywords).

        Args:
            db: Database session
            product: Product to update
            additional_keywords: Keywords to add
            remove_keywords: Keywords to remove

        Returns:
            Dictionary with update results
        """
        original_count = len(product.keywords)
        keywords_set = set(product.keywords)

        if additional_keywords:
            for kw in additional_keywords:
                keywords_set.add(kw)

        if remove_keywords:
            for kw in remove_keywords:
                keywords_set.discard(kw)

        product.keywords = list(keywords_set)
        await db.commit()
        await db.refresh(product)

        return {
            "product_id": str(product.id),
            "product_name": product.name,
            "action": "updated",
            "original_count": original_count,
            "new_count": len(product.keywords),
            "added": len(additional_keywords) if additional_keywords else 0,
            "removed": len(remove_keywords) if remove_keywords else 0,
            "keywords": product.keywords,
        }

    async def analyze_keyword_coverage(
        self,
        product: Product,
    ) -> dict[str, Any]:
        """
        Analyze keyword coverage and suggest improvements.

        Args:
            product: Product to analyze

        Returns:
            Dictionary with coverage analysis
        """
        keywords = product.keywords
        competitors = product.competitors

        # Categorize existing keywords
        analysis = {
            "product_id": str(product.id),
            "product_name": product.name,
            "total_keywords": len(keywords),
            "has_brand_variations": any(
                product.name.lower() in kw.lower() for kw in keywords
            ),
            "has_competitor_keywords": bool(competitors),
            "competitor_count": len(competitors),
            "has_problem_phrases": any(
                any(word in kw.lower() for word in ["how to", "why", "what"])
                for kw in keywords
            ),
            "recommendations": [],
        }

        # Generate recommendations
        if analysis["total_keywords"] < 5:
            analysis["recommendations"].append(
                "Consider generating more keywords for better coverage"
            )

        if not analysis["has_brand_variations"]:
            analysis["recommendations"].append(
                "Add brand name variations and common misspellings"
            )

        if not analysis["has_competitor_keywords"]:
            analysis["recommendations"].append(
                "Add competitor names for competitive intelligence"
            )

        if not analysis["has_problem_phrases"]:
            analysis["recommendations"].append(
                "Add problem-based phrases that your target audience searches for"
            )

        if analysis["total_keywords"] > 100:
            analysis["recommendations"].append(
                "Consider reducing keywords to focus on high-signal terms"
            )

        return analysis
