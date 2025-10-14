"""
Celery Application for intelligent-core Background Jobs
========================================================

Handles:
- Learning model updates (daily)
- Batch document analysis
- Scheduled predictions
- Heavy ML computations
"""
import os
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

# Redis backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/2")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5673/")

# Create Celery app
app = Celery(
    'intelligent-core',
    broker=RABBITMQ_URL,
    backend=REDIS_URL,
    include=[
        'tasks.learning_tasks',
        'tasks.batch_tasks',
        'tasks.prediction_tasks',
    ]
)

# Configuration
app.conf.update(
    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Result backend
    result_expires=3600 * 24 * 7,  # 7 days
    result_backend_transport_options={'master_name': 'mymaster'},

    # Task routing
    task_routes={
        'learning_tasks.*': {'queue': 'learning'},
        'batch_tasks.*': {'queue': 'batch'},
        'prediction_tasks.*': {'queue': 'prediction'},
    },

    # Performance
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Retry policy
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,

    # Rate limits
    task_default_rate_limit='100/m',

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Queues
app.conf.task_queues = (
    Queue('learning', Exchange('learning'), routing_key='learning',
          queue_arguments={'x-max-priority': 10}),
    Queue('batch', Exchange('batch'), routing_key='batch',
          queue_arguments={'x-max-priority': 5}),
    Queue('prediction', Exchange('prediction'), routing_key='prediction',
          queue_arguments={'x-max-priority': 7}),
    Queue('default', Exchange('default'), routing_key='default'),
)

# Beat schedule (cron jobs)
app.conf.beat_schedule = {
    # Daily learning model update at 2 AM
    'update-learning-models-daily': {
        'task': 'learning_tasks.update_all_models',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'learning', 'priority': 10}
    },

    # Hourly pattern extraction
    'extract-patterns-hourly': {
        'task': 'learning_tasks.extract_patterns',
        'schedule': crontab(minute=0),
        'options': {'queue': 'learning', 'priority': 7}
    },

    # Daily predictions at 6 AM
    'generate-predictions-daily': {
        'task': 'prediction_tasks.generate_daily_predictions',
        'schedule': crontab(hour=6, minute=0),
        'options': {'queue': 'prediction', 'priority': 8}
    },

    # Weekly full model retraining (Sunday 3 AM)
    'retrain-models-weekly': {
        'task': 'learning_tasks.full_model_retrain',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
        'options': {'queue': 'learning', 'priority': 10}
    },

    # Every 6 hours: cleanup old results
    'cleanup-old-results': {
        'task': 'batch_tasks.cleanup_old_results',
        'schedule': crontab(minute=0, hour='*/6'),
        'options': {'queue': 'default', 'priority': 1}
    },
}

if __name__ == '__main__':
    app.start()
