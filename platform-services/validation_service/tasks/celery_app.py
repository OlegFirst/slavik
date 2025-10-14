"""
Celery Application Configuration
"""

from celery import Celery
from celery.schedules import crontab
from config import settings

app = Celery(
    "validation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.kpi_collector",
        "tasks.kpi_alerting",
    ]
)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat Schedule (Periodic Tasks)
app.conf.beat_schedule = {
    # Daily KPI collection (runs at 2 AM UTC)
    "collect-all-kpis-daily": {
        "task": "tasks.kpi_collector.collect_all_kpis",
        "schedule": crontab(hour=2, minute=0),
    },
    # Hourly KPI threshold check
    "check-kpi-thresholds-hourly": {
        "task": "tasks.kpi_alerting.check_kpi_thresholds_hourly",
        "schedule": crontab(minute=0),  # Every hour on the hour
    },
    # Daily auto-resolve alerts
    "auto-resolve-alerts-daily": {
        "task": "tasks.kpi_alerting.auto_resolve_alerts",
        "schedule": crontab(hour=3, minute=0),  # 3 AM UTC
    },
}

if __name__ == "__main__":
    app.start()
