"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AsyncSessionDep
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns a simple status to confirm the API is running.
    """
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(db: AsyncSessionDep) -> HealthResponse:
    """
    Readiness check that verifies database connectivity.

    This endpoint checks if the application is ready to serve traffic
    by verifying connections to required services.
    """
    # Check database connection
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        return HealthResponse(status=f"database_error: {e}")

    # TODO: Check Redis connection when implemented

    return HealthResponse(status="ready")
