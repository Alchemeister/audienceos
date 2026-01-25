"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1 import audiences, billing, campaigns, feedback, health, insights, products, tracking, webhooks
from app.core.config import get_settings
from app.core.exceptions import (
    AIServiceError,
    AudienceOSError,
    AuthenticationError,
    AuthorizationError,
    ExternalAPIError,
    NotFoundError,
    RateLimitError,
    TierLimitError,
    ValidationError,
)
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting AudienceOS API in {settings.APP_ENV} mode")

    # Auto-create tables in development mode
    if settings.APP_ENV == "development":
        from app.db.session import async_engine
        from app.models.base import Base
        # Import all models to register them
        from app.models import (  # noqa: F401
            Organization,
            User,
            Product,
            AudienceSource,
            AudienceResearch,
            FeedbackItem,
            Campaign,
            GeneratedPost,
            TrackedLink,
            ClickEvent,
            DeepAnalysis,
            FeedbackTheme,
            Insight,
            WeeklyReport,
            Subscription,
            UsageRecord,
            BillingEvent,
            KeywordSearchState,
        )

        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created (development mode)")

        # Seed dev organization if it doesn't exist
        from app.db.session import AsyncSessionLocal
        from sqlalchemy import select
        import uuid

        async with AsyncSessionLocal() as session:
            dev_org_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
            result = await session.execute(
                select(Organization).where(Organization.id == dev_org_id)
            )
            existing_org = result.scalar_one_or_none()

            if not existing_org:
                from app.models.user import SubscriptionTier
                dev_org = Organization(
                    id=dev_org_id,
                    name="Dev Organization",
                    subscription_tier=SubscriptionTier.PRO,
                    deep_analysis_credits=4,
                )
                session.add(dev_org)
                await session.commit()
                logger.info("Dev organization seeded")

    yield
    # Shutdown
    logger.info("Shutting down AudienceOS API")


# Create FastAPI app
app = FastAPI(
    title="AudienceOS API",
    description="B2B SaaS for audience research and feedback aggregation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        settings.APP_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "not_found", "message": exc.message, "details": exc.details},
    )


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "message": exc.message, "details": exc.details},
    )


@app.exception_handler(AuthenticationError)
async def auth_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "authentication_error", "message": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(AuthorizationError)
async def authz_handler(request: Request, exc: AuthorizationError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": "authorization_error", "message": exc.message},
    )


@app.exception_handler(RateLimitError)
async def rate_limit_handler(request: Request, exc: RateLimitError):
    headers = {}
    if exc.details.get("retry_after"):
        headers["Retry-After"] = str(exc.details["retry_after"])
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "rate_limit", "message": exc.message, "details": exc.details},
        headers=headers,
    )


@app.exception_handler(TierLimitError)
async def tier_limit_handler(request: Request, exc: TierLimitError):
    return JSONResponse(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        content={"error": "tier_limit", "message": exc.message, "details": exc.details},
    )


@app.exception_handler(AIServiceError)
async def ai_service_handler(request: Request, exc: AIServiceError):
    logger.error(f"AI service error: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "ai_service_error",
            "message": "AI service temporarily unavailable",
            "details": {"provider": exc.details.get("provider")},
        },
    )


@app.exception_handler(ExternalAPIError)
async def external_api_handler(request: Request, exc: ExternalAPIError):
    logger.error(f"External API error: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "external_api_error",
            "message": "External service temporarily unavailable",
            "details": {"service": exc.details.get("service")},
        },
    )


@app.exception_handler(AudienceOSError)
async def generic_handler(request: Request, exc: AudienceOSError):
    logger.error(f"Application error: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_error", "message": exc.message},
    )


# Include routers
app.include_router(health.router)
app.include_router(products.router, prefix="/api/v1")
app.include_router(audiences.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(campaigns.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(tracking.router)  # Has its own prefixes for /aos/{short_code} redirect


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AudienceOS API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "disabled",
    }
# force reload
