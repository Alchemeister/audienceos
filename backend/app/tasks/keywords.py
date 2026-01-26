"""Background tasks for automatic keyword generation."""

import asyncio
import logging
from typing import Any

from celery import shared_task
from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.product import Product
from app.services.keywords import KeywordGenerationService

logger = logging.getLogger(__name__)


def run_async(coro):
    """Run async function in sync context for Celery."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(bind=True, max_retries=3)
def generate_keywords_for_product(
    self,
    product_id: str,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """
    Generate keywords for a product using AI.

    This task is automatically triggered when:
    1. A new product is created
    2. A product's description is significantly updated
    3. Manually requested via API

    Args:
        product_id: UUID of the product
        force_regenerate: Force regeneration even if keywords exist

    Returns:
        Dictionary with generation results
    """
    return run_async(_generate_keywords_for_product(product_id, force_regenerate))


async def _generate_keywords_for_product(
    product_id: str,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """Async implementation of keyword generation."""
    async with async_session_factory() as db:
        # Get product
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()

        if not product:
            return {"error": "Product not found", "product_id": product_id}

        # Generate keywords
        service = KeywordGenerationService()
        generation_result = await service.generate_keywords_for_product(
            db, product, force_regenerate=force_regenerate
        )

        logger.info(
            f"Keyword generation complete for {product.name}: "
            f"{generation_result.get('total_keywords', 0)} keywords generated"
        )

        return generation_result


@shared_task(bind=True)
def regenerate_keywords_for_all_products(self) -> dict[str, Any]:
    """
    Regenerate keywords for all products that don't have keywords.

    Useful for:
    - Initial migration when adding keyword generation feature
    - Batch processing of products without keywords
    - Maintenance task to ensure all products have good coverage

    Returns:
        Summary of regeneration results
    """
    return run_async(_regenerate_keywords_for_all_products())


async def _regenerate_keywords_for_all_products() -> dict[str, Any]:
    """Async implementation of bulk regeneration."""
    async with async_session_factory() as db:
        # Get all products without keywords or with fewer than 3 keywords
        result = await db.execute(
            select(Product)
        )
        all_products = result.scalars().all()

        # Filter products that need keyword generation
        products_needing_keywords = [
            p for p in all_products if not p.keywords or len(p.keywords) < 3
        ]

        logger.info(
            f"Starting bulk keyword generation for {len(products_needing_keywords)} products"
        )

        service = KeywordGenerationService()
        results = {
            "total_products": len(all_products),
            "products_needing_keywords": len(products_needing_keywords),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "results": [],
        }

        for product in products_needing_keywords:
            try:
                # Create a new session for each product to avoid issues
                async with async_session_factory() as product_db:
                    result = await product_db.execute(
                        select(Product).where(Product.id == product.id)
                    )
                    fresh_product = result.scalar_one()

                    generation_result = await service.generate_keywords_for_product(
                        product_db, fresh_product, force_regenerate=False
                    )

                    results["results"].append({
                        "product_id": str(fresh_product.id),
                        "product_name": fresh_product.name,
                        "keywords_generated": generation_result.get("total_keywords", 0),
                        "status": "success",
                    })

                    results["processed"] += 1
                    results["successful"] += 1

            except Exception as e:
                logger.error(f"Error generating keywords for {product.name}: {e}")
                results["results"].append({
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "status": "failed",
                    "error": str(e),
                })
                results["processed"] += 1
                results["failed"] += 1

        logger.info(
            f"Bulk keyword generation complete: "
            f"processed {results['processed']}, "
            f"successful {results['successful']}, "
            f"failed {results['failed']}"
        )

        return results


@shared_task
def trigger_keyword_generation_for_new_product(product_id: str) -> dict[str, Any]:
    """
    Triggered when a new product is created.

    Automatically generates keywords to improve monitoring coverage.

    Args:
        product_id: UUID of the newly created product

    Returns:
        Task status information
    """
    task = generate_keywords_for_product.delay(product_id, force_regenerate=False)

    return {
        "product_id": product_id,
        "keyword_generation_task_id": task.id,
        "status": "queued",
        "message": "Automatic keyword generation queued",
    }
