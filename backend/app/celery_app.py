"""
Celery application configuration for AI Podcast Platform
"""

from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "podcast_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.podcast_tasks",
        "app.tasks.tts_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # Soft limit 50 minutes
    # Result backend
    result_expires=3600 * 24,  # Results expire after 24 hours
    result_backend=settings.CELERY_RESULT_BACKEND,
    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    # Worker settings
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    # Task retry settings
    task_default_retry_delay=60,  # Retry after 1 minute
    task_max_retries=3,  # Max 3 retries
    # Queue settings
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "high_priority": {
            "exchange": "high_priority",
            "routing_key": "high_priority",
        },
        "low_priority": {
            "exchange": "low_priority",
            "routing_key": "low_priority",
        },
    },
    # Task routes
    task_routes={
        "app.tasks.podcast_tasks.process_podcast": {"queue": "high_priority"},
        "app.tasks.tts_tasks.synthesize_speech": {"queue": "default"},
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])
