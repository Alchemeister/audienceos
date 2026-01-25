"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "audienceos",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.feedback",
        "app.tasks.monitoring",
        "app.tasks.insights",
        "app.tasks.billing",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,  # Acknowledge task after completion for reliability
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # One task at a time for predictable execution

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour

    # Task time limits
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit

    # Retry settings
    task_default_retry_delay=60,  # 1 minute default retry delay
    task_max_retries=3,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Monitor mentions every 15 minutes
    "monitor-mentions-every-15-min": {
        "task": "app.tasks.monitoring.monitor_all_products",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "monitoring"},
    },
    # Clean up old click events daily (keep 90 days)
    "cleanup-old-events-daily": {
        "task": "app.tasks.monitoring.cleanup_old_events",
        "schedule": crontab(hour=3, minute=0),  # 3 AM UTC
        "options": {"queue": "maintenance"},
    },
    # Generate weekly reports every Monday at 6 AM UTC
    "generate-weekly-reports-monday": {
        "task": "app.tasks.insights.generate_all_weekly_reports",
        "schedule": crontab(hour=6, minute=0, day_of_week="monday"),
        "options": {"queue": "insights"},
    },
    # Reset deep analysis credits on the 1st of each month
    "reset-monthly-credits": {
        "task": "app.tasks.insights.reset_monthly_credits",
        "schedule": crontab(hour=0, minute=0, day_of_month=1),
        "options": {"queue": "maintenance"},
    },
    # Reset monthly usage counters on the 1st of each month
    "reset-monthly-usage": {
        "task": "app.tasks.billing.reset_all_monthly_usage",
        "schedule": crontab(hour=0, minute=5, day_of_month=1),
        "options": {"queue": "billing"},
    },
    # Reset deep analysis credits on the 1st of each month (billing version)
    "reset-deep-analysis-credits": {
        "task": "app.tasks.billing.reset_deep_analysis_credits",
        "schedule": crontab(hour=0, minute=10, day_of_month=1),
        "options": {"queue": "billing"},
    },
    # Process subscription period ends daily
    "process-subscription-ends": {
        "task": "app.tasks.billing.process_subscription_period_ends",
        "schedule": crontab(hour=1, minute=0),  # 1 AM UTC daily
        "options": {"queue": "billing"},
    },
    # Check usage limits daily and warn if approaching
    "check-usage-limits": {
        "task": "app.tasks.billing.check_usage_limits",
        "schedule": crontab(hour=12, minute=0),  # Noon UTC daily
        "options": {"queue": "billing"},
    },
}

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.monitoring.*": {"queue": "monitoring"},
    "app.tasks.feedback.*": {"queue": "feedback"},
    "app.tasks.insights.*": {"queue": "insights"},
    "app.tasks.billing.*": {"queue": "billing"},
}


# Optional: Auto-discover tasks from modules
# celery_app.autodiscover_tasks(["app.tasks"])
