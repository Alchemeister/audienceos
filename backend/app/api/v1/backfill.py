"""API endpoints for historical backfill management."""

import logging
from typing import Any
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.tasks.backfill import enhanced_historical_backfill
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{product_id}/backfill")
async def trigger_backfill(
    product_id: UUID,
    days: int | None = None,
    sources: list[str] | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Trigger historical backfill for a product.

    This endpoint starts a background task to search for and analyze
    historical mentions of your product across selected sources.

    **Features:**
    - Progress tracking (check status with task_id)
    - Intelligent rate limit handling
    - Deduplication across runs
    - Configurable time range and sources

    **Arguments:**
    - days: Number of days to backfill (default: based on subscription tier)
    - sources: List of sources to backfill from (default: ["reddit", "hackernews"])

    **Subscription Limits:**
    - Indie: 14 days, Reddit only
    - Pro: 90 days, Reddit + HackerNews
    - Agency: 180 days, Reddit + HackerNews
    """
    # Get product and verify ownership
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or access denied",
        )

    # Validate sources
    valid_sources = ["reddit", "hackernews"]
    if sources:
        invalid = [s for s in sources if s not in valid_sources]
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sources: {invalid}. Valid sources: {valid_sources}",
            )

    # Queue backfill task
    task = enhanced_historical_backfill.delay(
        str(product_id),
        days=days,
        sources=sources,
    )

    return {
        "message": "Historical backfill started",
        "task_id": task.id,
        "product_id": str(product_id),
        "product_name": product.name,
        "backfill_days": days or "tier_default",
        "sources": sources or "tier_default",
        "status_url": f"/api/v1/backfill/task/{task.id}",
    }


@router.get("/task/{task_id}")
async def get_backfill_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Get the status of a backfill task.

    Returns:
    - state: PENDING, PROGRESS, SUCCESS, FAILURE
    - progress: 0-100 percentage (if in PROGRESS)
    - result: Final results (if SUCCESS)
    - error: Error message (if FAILURE)
    """
    task = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "state": task.state,
    }

    if task.state == "PENDING":
        response["status"] = "Task is waiting to start"

    elif task.state == "PROGRESS":
        # Task is running - get progress info
        info = task.info or {}
        response.update({
            "progress": info.get("progress", 0),
            "stage": info.get("stage", "unknown"),
            "product_id": info.get("product_id"),
            "product_name": info.get("product_name"),
            "current_query": info.get("current_query"),
        })

    elif task.state == "SUCCESS":
        # Task completed successfully
        result = task.result or {}
        response.update({
            "status": "completed",
            "result": result,
        })

    elif task.state == "FAILURE":
        # Task failed
        response.update({
            "status": "failed",
            "error": str(task.info),
        })

    else:
        response["status"] = f"Unknown state: {task.state}"

    return response


@router.get("/{product_id}/status")
async def get_product_backfill_status(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get backfill status for a product.

    Shows when the product was last backfilled and its current
    feedback collection status.
    """
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or access denied",
        )

    return {
        "product_id": str(product.id),
        "product_name": product.name,
        "backfill_completed_at": (
            product.backfill_completed_at.isoformat()
            if product.backfill_completed_at
            else None
        ),
        "feedback_last_collected_at": (
            product.feedback_last_collected_at.isoformat()
            if product.feedback_last_collected_at
            else None
        ),
        "has_completed_backfill": product.backfill_completed_at is not None,
        "is_actively_monitored": product.feedback_last_collected_at is not None,
    }
